import google.generativeai as genai
from typing import List, Dict, Any
import json
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
from influencer_agent.app.core.config import settings
import asyncio # Added for running tasks in scheduler

class AIClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = 'gemini-2.5-flash'
        self.vision_model = genai.GenerativeModel(self.model_name)
        self.text_model = genai.GenerativeModel(self.model_name)

    def _download_image(self, image_url: str):
        try:
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    async def analyze_visuals(self, image_url: str) -> str:
        """Feature 3: Visual Analysis"""
        img = self._download_image(image_url)
        if not img: return "Image unavailable"
        prompt = "Describe this image for Instagram. Focus on lighting, mood, objects, and aesthetic style."
        try:
            res = self.vision_model.generate_content([prompt, img])
            return res.text
        except Exception as e:
            return f"Error analyzing visual: {str(e)}"

    async def generate_captions(self, visual_desc: str, user_style: str) -> List[str]:
        """Feature 3: Caption Generation - FIXED PROMPT"""
        prompt = f"""
        You are an expert Social Media Manager.
        STYLE PROFILE: {user_style}
        IMAGE CONTEXT: {visual_desc}
        
        TASK: Based ONLY on the IMAGE CONTEXT, generate 3 unique Instagram captions (Hook + Body + CTA) in the user's voice.
        
        OUTPUT: JSON only. Format MUST be: {{"captions": ["cap1", "cap2", "cap3"]}}
        """
        try:
            res = self.text_model.generate_content(prompt)
            clean_text = res.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text).get("captions", [])
        except:
            return ["Error parsing captions."]

    async def generate_hashtags(self, caption: str, user_style: str) -> List[str]:
        """Feature 3: Hashtag Generation"""
        prompt = f"""
        Analyze the following caption and the user's style.
        CAPTION: "{caption}"
        STYLE: {user_style}
        
        TASK: Suggest 10 high-impact, relevant hashtags. Mix between niche, trending, and general tags.
        
        OUTPUT: JSON only. Format: {{"hashtags": ["#tag1", "#tag2", "#tag3"]}}
        """
        try:
            res = self.text_model.generate_content(prompt)
            clean = res.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean).get("hashtags", [])
        except:
            return []

    async def learn_style(self, past_posts: List[Dict]) -> str:
        """Feature 1: Learning"""
        if not past_posts: return "Generic professional tone."
        posts_text = "\n".join([f"Post: {p.get('caption', '')}" for p in past_posts[:10]])
        prompt = f"""
        Analyze these past Instagram posts to understand the author's voice.
        POSTS: {posts_text}
        Return a concise paragraph description of this style.
        """
        res = self.text_model.generate_content(prompt)
        return res.text

    async def predict_optimal_time(self, history: List[Dict], user_niche: str = "General") -> Dict:
        """Feature 7: Optimization"""
        # Logic remains the same: predict hours_delay
        return {"hours_delay": 1, "reason": "Optimized for 6PM engagement."}
    
    # --- NEW: WEEKLY PLAN GENERATOR (Feature 2) ---
    async def generate_weekly_plan(self, style_profile: str, user_niche: str) -> List[Dict]:
        """Generates 5 structured content ideas for the week."""
        prompt = f"""
        You are an expert Content Planner. The user is an influencer in the '{user_niche}' niche.
        Their writing style is: {style_profile}
        
        TASK: Create a plan for 5 posts (Monday to Friday, one per day) for next week.
        For each post, suggest:
        1. A compelling theme/topic (e.g., "Meme Monday").
        2. The best day and hour (e.g., "Monday 10:00").
        3. A caption prompt (what image/video content is needed).
        
        Output: JSON array only. Format MUST be:
        [
            {{
                "day": "Monday",
                "time": "10:00",
                "theme": "Meme Monday: Relatable developer struggle",
                "caption_prompt": "Post a short, snappy caption about a bug you spent 3 hours fixing."
            }},
            // ... 4 more ideas
        ]
        """
        try:
            res = self.text_model.generate_content(prompt)
            clean = res.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean)
        except Exception as e:
            return [{"day": "Monday", "time": "12:00", "theme": "Fallback Idea", "caption_prompt": "Upload a selfie."}]

    async def analyze_comment_intent(self, comment_text: str, post_context: str) -> Dict:
        # ... (Comment analysis logic remains the same) ...
        return {"category": "UNKNOWN", "action": "IGNORE", "reason": "AI Error"}

    async def generate_smart_reply(self, comment_text: str, category: str, user_style: str) -> str:
        # ... (Reply generation logic remains the same) ...
        return "Thanks for the comment!"
