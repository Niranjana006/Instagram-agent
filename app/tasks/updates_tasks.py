from celery import shared_task
import requests
from influencer_agent.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(name="refresh_token_task")
def refresh_token_task():
   
    try:
        url = "https://graph.instagram.com/refresh_access_token"
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": settings.INSTAGRAM_ACCESS_TOKEN
        }
        res = requests.get(url, params=params)
        data = res.json()
        
        if "access_token" in data:
            new_token = data["access_token"]
            # In a real app, update this in the Database (InstagramAccount table)
            # For local .env, we log it so you can update it manually if needed
            logger.info(f"Token Refreshed! Expires in {data.get('expires_in')} seconds.")
        else:
            logger.error(f"Token refresh failed: {data}")
            
    except Exception as e:
        logger.error(f"Refresh task error: {e}")
