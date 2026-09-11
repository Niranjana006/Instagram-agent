from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from influencer_agent.app.db.session import SessionLocal
from influencer_agent.app.models.content_plan import ContentPlan, ContentStatus
from influencer_agent.app.models.user import User
from influencer_agent.app.services.instagram_service import InstagramService
from influencer_agent.app.ai.multimodal import AIClient
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def next_weekday(d, weekday):
    """Calculates the date of the next given weekday (0=Mon, 6=Sun)"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days=days_ahead)

@shared_task(name="weekly_planning_task")
def weekly_planning_task(user_id: int):
    """
    Feature 2: Creates a content calendar for the next 7 days using AI.
    """
    db: Session = next(get_db())
    try:
        ai = AIClient()
        service = InstagramService()
        
        # 1. Get User Style Profile (from Onboarding)
        # In a real app, this would be stored on the CreatorProfile model.
        # For now, we'll quickly learn it based on past posts:
        recent_posts = service.get_recent_posts(limit=10)
        style_profile = asyncio.run(ai.learn_style(recent_posts))
        
        user_niche = "Tech/Lifestyle" # Hardcoded niche for now

        # 2. Generate Plan from AI
        logger.info(f"Generating weekly plan for User {user_id} using style: {style_profile[:30]}...")
        raw_plan = asyncio.run(ai.generate_weekly_plan(style_profile, user_niche))

        # 3. Process and Save Drafts
        plans_created = 0
        
        # Start planning from next Monday
        today = datetime.utcnow().date()
        
        for idea in raw_plan:
            try:
                # Calculate the exact date and time for scheduling
                day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
                
                day_name = idea['day']
                time_str = idea['time'].split(':') # e.g., "10:00" -> ["10", "00"]
                
                plan_date = next_weekday(today, day_map[day_name])
                
                # Combine date and time
                scheduled_dt = datetime(
                    plan_date.year, plan_date.month, plan_date.day,
                    hour=int(time_str[0]), minute=int(time_str[1])
                )
                
                # Create a DRAFT post in the database
                new_plan = ContentPlan(
                    user_id=user_id,
                    instagram_account_id=1, # Hardcoded ID
                    caption_generated=idea['caption_prompt'],
                    caption_final=f"DRAFT: {idea['caption_prompt']}",
                    media_type="IMAGE", # Assume image for planning
                    scheduled_time=scheduled_dt,
                    status=ContentStatus.DRAFT,
                    performance_analysis=f"AI Theme: {idea['theme']}"
                )
                db.add(new_plan)
                plans_created += 1
            except Exception as e:
                logger.error(f"Error saving plan idea: {e}")
        
        db.commit()
        return f"Weekly plan created: {plans_created} draft post(s) generated."

    except Exception as e:
        logger.error(f"Planning failed: {e}")
        return f"Planning failed: {str(e)}"
    finally:
        db.close()
