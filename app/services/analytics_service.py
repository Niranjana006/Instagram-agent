from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from influencer_agent.app.models.content_plan import ContentPlan, ContentStatus
from influencer_agent.app.ai.multimodal import AIClient
import json

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_weekly_report(self):
        
        # 1. Fetch Data
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        posts = self.db.query(ContentPlan).filter(
            ContentPlan.created_at >= seven_days_ago
        ).all()

        if not posts:
            return {
                "summary": "No posts found in the last 7 days.",
                "stats": {"total_posts": 0, "total_likes": 0}
            }

        # 2. Calculate Stats
        total_likes = 0
        total_comments = 0
        top_post = None
        top_likes = -1
        
        posts_data_for_ai = []

        for post in posts:
            # Parse snapshots if they exist, or rely on latest scrape
            snapshots = post.engagement_snapshots or {}
            # Get latest snapshot values
            latest_metrics = {"likes": 0, "comments": 0}
            if snapshots:
                # Get the last key (latest timestamp)
                latest_key = list(snapshots.keys())[-1]
                latest_metrics = snapshots[latest_key]
            
            likes = latest_metrics.get("likes", 0)
            comments = latest_metrics.get("comments", 0)
            
            total_likes += likes
            total_comments += comments
            
            if likes > top_likes:
                top_likes = likes
                top_post = post.caption_final or "No Caption"

            # FIXED: Handle NoneType for scheduled_time safely
            date_str = "Unknown Date"
            if post.scheduled_time:
                date_str = post.scheduled_time.strftime("%Y-%m-%d")
            elif post.created_at:
                date_str = post.created_at.strftime("%Y-%m-%d")

            posts_data_for_ai.append({
                "date": date_str,
                "type": post.media_type or "IMAGE",
                "likes": likes,
                "comments": comments,
                "hashtags": post.hashtags or []
            })

        # 3. Ask AI for Strategy
        ai = AIClient()
        prompt = f"""
        You are a Senior Social Media Analyst.
        Here is the performance data for the last 7 days:
        
        TOTAL POSTS: {len(posts)}
        TOTAL LIKES: {total_likes}
        TOTAL COMMENTS: {total_comments}
        
        POST DETAILS:
        {json.dumps(posts_data_for_ai, indent=2)}
        
        TASK: Write a 'Weekly Strategy Report'.
        1. Highlight the Top Performing post and explain WHY it might have worked.
        2. Identify any patterns (e.g. "Video performed better than Image").
        3. Give 3 concrete recommendations for next week.
        
        Keep it professional but encouraging.
        """
        
        try:
            # We use the text model for this analysis
            res = ai.text_model.generate_content(prompt)
            report_text = res.text
        except Exception as e:
            report_text = f"AI Analysis failed: {str(e)}"

        return {
            "period": "Last 7 Days",
            "stats": {
                "posts": len(posts),
                "likes": total_likes,
                "comments": total_comments,
                "avg_engagement": round((total_likes + total_comments) / len(posts), 2) if len(posts) > 0 else 0
            },
            "ai_report": report_text
        }
