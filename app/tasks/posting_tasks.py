from celery import shared_task
from datetime import datetime
import time
from sqlalchemy.orm import Session
from influencer_agent.app.db.session import SessionLocal
from influencer_agent.app.models.content_plan import ContentPlan, ContentStatus
from influencer_agent.app.services.instagram_service import InstagramService
from influencer_agent.app.models.instagram_account import InstagramAccount
import logging

logger = logging.getLogger(__name__)

@shared_task(name="publish_post_task", bind=True, max_retries=3)
def publish_post_task(self, plan_id: int):
    
    db: Session = SessionLocal()
    try:
        # 1. Get the plan from DB
        plan = db.query(ContentPlan).filter(ContentPlan.id == plan_id).first()
        if not plan:
            logger.error(f"Plan {plan_id} not found")
            return "Plan not found"

        if plan.status != ContentStatus.SCHEDULED:
            logger.warning(f"Plan {plan_id} is not SCHEDULED (Status: {plan.status})")
            return "Skipped"

        # 2. Get Instagram Credentials 
        # (In a real multi-user app, we fetch from plan.instagram_account.access_token)
        service = InstagramService() 
        
        # 3. Step 1: Create Container
        logger.info(f"Uploading media for Plan {plan_id}...")
        container_id = service.create_container(plan.media_url, plan.caption_final)
        
        # Wait briefly for processing
        time.sleep(5) 
        
        # 4. Step 2: Publish
        logger.info(f"Publishing container {container_id}...")
        media_id = service.publish_container(container_id)

        # 5. Success! Update DB
        plan.status = ContentStatus.PUBLISHED
        # We store the live media ID for tracking later (assuming we add a column or use snapshots)
        plan.updated_at = datetime.utcnow()
        db.commit()

        # 6. Trigger Feature 5: Schedule Tracking
        # Track at: 5m, 30m, 60m, 4h (240m), 24h (1440m)
        delays = [5, 30, 60, 240, 1440] 
        for minutes in delays:
            # countdown is in seconds
            track_engagement_task.apply_async((plan_id, media_id), countdown=minutes*60)

        return f"Published successfully: {media_id}"

    except Exception as e:
        logger.error(f"Posting failed: {e}")
        plan.status = ContentStatus.FAILED
        db.commit()
        # Retry in 5 minutes if it was a network error
        raise self.retry(exc=e, countdown=300)
    finally:
        db.close()

@shared_task(name="track_engagement_task")
def track_engagement_task(plan_id: int, media_id: str):
   
    db: Session = SessionLocal()
    try:
        plan = db.query(ContentPlan).filter(ContentPlan.id == plan_id).first()
        if not plan: return

        service = InstagramService()
        metrics = service.get_media_analytics(media_id)
        
        # Save snapshot
        current_snapshots = dict(plan.engagement_snapshots) if plan.engagement_snapshots else {}
        timestamp = datetime.utcnow().isoformat()
        current_snapshots[timestamp] = metrics
        
        plan.engagement_snapshots = current_snapshots
        db.commit()
        logger.info(f"Tracked metrics for {plan_id}: {metrics['likes']} likes")
        
    except Exception as e:
        logger.error(f"Tracking failed: {e}")
    finally:
        db.close()
