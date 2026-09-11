import requests
from typing import Dict, List, Any
from datetime import datetime
from influencer_agent.app.core.config import settings

class InstagramService:
    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, access_token=None, account_id=None):
        self.access_token = access_token or settings.INSTAGRAM_ACCESS_TOKEN
        self.account_id = account_id or settings.INSTAGRAM_ACCOUNT_ID

    def get_recent_posts(self, limit: int = 20) -> List[Dict]:
        """Feature 1: Fetch history for learning style"""
        url = f"{self.BASE_URL}/{self.account_id}/media"
        params = {
            "fields": "caption,media_type,media_url,timestamp,like_count,comments_count",
            "limit": limit,
            "access_token": self.access_token
        }
        res = requests.get(url, params=params)
        return res.json().get("data", [])
        
    def get_media_caption(self, media_id: str) -> str:
        """Fetches the original caption of a post to give context to the AI."""
        url = f"{self.BASE_URL}/{media_id}"
        params = {"fields": "caption", "access_token": self.access_token}
        try:
            res = requests.get(url, params=params)
            return res.json().get("caption", "")
        except:
            return ""

    def create_container(self, image_url: str, caption: str) -> str:
        """Feature 4: Smart Posting (Step 1 - Upload)"""
        url = f"{self.BASE_URL}/{self.account_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        res = requests.post(url, data=payload)
        try:
            res.raise_for_status()
            return res.json()["id"]
        except Exception as e:
            print(f"IG Upload Error: {res.text}")
            raise e

    def publish_container(self, creation_id: str) -> str:
        """Feature 4: Smart Posting (Step 2 - Publish)"""
        url = f"{self.BASE_URL}/{self.account_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        res = requests.post(url, data=payload)
        try:
            res.raise_for_status()
            return res.json()["id"]
        except Exception as e:
            print(f"IG Publish Error: {res.text}")
            raise e

    def get_media_analytics(self, media_id: str) -> Dict:
        """Feature 5: Real-time Tracking"""
        url_public = f"{self.BASE_URL}/{media_id}"
        params_public = {
            "fields": "like_count,comments_count",
            "access_token": self.access_token
        }
        
        try:
            public_res = requests.get(url_public, params=params_public)
            public_data = public_res.json()
            
            return {
                "likes": public_data.get("like_count", 0),
                "comments": public_data.get("comments_count", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Analytics Error: {e}")
            return {"likes": 0, "comments": 0}

    # --- COMMENT ACTIONS ---
    
    def reply_to_comment(self, comment_id: str, message: str):
        url = f"{self.BASE_URL}/{comment_id}/replies"
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            print(f"Failed to reply: {res.text}")

    def hide_comment(self, comment_id: str):
        url = f"{self.BASE_URL}/{comment_id}"
        payload = {
            "hide": True,
            "access_token": self.access_token
        }
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            print(f"Failed to hide: {res.text}")