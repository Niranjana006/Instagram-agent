from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from influencer_agent.app.core.config import settings
from influencer_agent.app.db.session import SessionLocal
from influencer_agent.app.tasks.posting_tasks import publish_post_task
from influencer_agent.app.tasks.moderation_tasks import process_comment_task
from influencer_agent.app.ai.multimodal import AIClient
from influencer_agent.app.schemas.instagram import PostSchedule, ScheduleMode
from influencer_agent.app.models.content_plan import ContentPlan, ContentStatus
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

router = APIRouter()

class PostCreate(BaseModel):
    image_url: str
    caption_context: str = ""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.WEBHOOK_VERIFY_TOKEN:
        return int(params.get("hub.challenge"))
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def handle_webhook(request: Request):
    # --- DEBUGGING START ---
    raw_body = await request.body()
    print("\n🔥 WEBHOOK HIT! RAW DATA RECEIVED:")
    print(raw_body.decode('utf-8'))
    print("-" * 50)
    # --- DEBUGGING END ---

    data = await request.json()
    
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                field = change.get("field")
                val = change.get("value")
                
                print(f"👀 Checking field: {field}")
                
                if field == "comments":
                    text = val.get("text")
                    comment_id = val.get("id")
                    # Handle different media object structures
                    media = val.get("media", {})
                    # Sometimes it's a dict, sometimes just an ID string
                    if isinstance(media, dict):
                        media_id = media.get("id")
                    else:
                        media_id = media
                    
                    print(f"📝 Parsed: Text='{text}', ID={comment_id}, Media={media_id}")

                    if text and comment_id and media_id:
                        print(f"🚀 SENDING TO WORKER NOW...")
                        process_comment_task.delay(comment_id, text, media_id)
                    else:
                        print("❌ MISSING DATA - Cannot process.")
                        
    except Exception as e:
        print(f"❌ CRITICAL ERROR parsing webhook: {e}")
        import traceback
        traceback.print_exc()
        
    return {"status": "received"}

@router.post("/generate-captions")
async def generate_captions_endpoint(payload: PostCreate):
    ai = AIClient()
    user_style = "Sarcastic and uses lots of rocket emojis."
    captions = await ai.generate_captions(payload.caption_context, user_style)
    hashtags = []
    if captions:
        hashtags = await ai.generate_hashtags(captions[0], user_style)
    media_type = "VIDEO" if payload.image_url.lower().endswith(('.mp4', '.mov')) else "IMAGE"
    return {"captions": captions, "suggested_hashtags": hashtags, "media_type": media_type}

@router.post("/schedule-post")
async def schedule_post_endpoint(post_data: PostSchedule, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    final_delay = 0
    ai_note = "User selected immediate/manual."
    
    if post_data.mode == ScheduleMode.MANUAL:
        final_delay = post_data.manual_hours_delay
    elif post_data.mode == ScheduleMode.AUTO_AI:
        # Mock logic to keep it simple for now
        final_delay = 1
        ai_note = "AI Analysis: Optimized for engagement."

    scheduled_time = now
    if final_delay > 0:
        scheduled_time = now + timedelta(hours=final_delay)
        
    final_caption = post_data.caption_final
    if post_data.hashtags:
        final_caption += "\\n\\n" + " ".join(post_data.hashtags)

    new_plan = ContentPlan(
        media_url=post_data.image_url,
        caption_final=final_caption,
        caption_generated=post_data.caption_generated,
        hashtags=post_data.hashtags,
        media_type=post_data.media_type,
        status=ContentStatus.SCHEDULED,
        scheduled_time=scheduled_time,
        instagram_account_id=1, 
        user_id=1,
        performance_analysis=ai_note
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    publish_post_task.apply_async(args=[new_plan.id], eta=scheduled_time)
    
    return {
        "status": "scheduled", 
        "mode": post_data.mode,
        "ai_analysis": ai_note,
        "posting_at": scheduled_time.isoformat()
    }