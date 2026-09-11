from celery import shared_task
from influencer_agent.app.services.instagram_service import InstagramService
from influencer_agent.app.ai.multimodal import AIClient
import asyncio
import logging

logger = logging.getLogger(__name__)

# FIXED: Added 'media_id' to the function arguments to match the API call
@shared_task(name="process_comment_task")
def process_comment_task(comment_id: str, comment_text: str, media_id: str):
    
    try:
        service = InstagramService()
        ai = AIClient()
        
        logger.info(f"Analyzing comment {comment_id}: {comment_text}")
        
        # 1. Context: What post is this on?
        # We fetch the original caption so the AI knows what the user is commenting about
        post_caption = service.get_media_caption(media_id)
        
        # 2. Brain: What should we do?
        # Note: asyncio.run calls the async AI function synchronously for Celery
        analysis = asyncio.run(ai.analyze_comment_intent(comment_text, post_caption))
        
        action = analysis.get("action")
        category = analysis.get("category")
        
        logger.info(f"AI Verdict: [{category}] -> {action}")
        
        if action == "IGNORE":
            logger.info("DEBUG: Forcing reply for testing purposes.")
            action = "REPLY"
            category = "PRAISE"
            
        # 3. Action Execution
        if action == "HIDE":
            service.hide_comment(comment_id)
            logger.info(f"HIDDEN: Toxic comment detected.")
            
        elif action == "REPLY":
            # In a real app, you would fetch the specific user's style from the DB here.
            # For now, we use a consistent persona.
            user_style = "Professional but friendly. Use emojis."
            
            reply_text = asyncio.run(ai.generate_smart_reply(comment_text, category, user_style))
            
            service.reply_to_comment(comment_id, reply_text)
            logger.info(f"REPLIED: {reply_text}")
            
        else:
            logger.info("IGNORED: Low priority or neutral comment.")
            
    except Exception as e:
        logger.error(f"Moderation Error: {e}")
