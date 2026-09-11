from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from influencer_agent.app.db.base import Base

class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class ContentPlan(Base):
    __tablename__ = "content_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    instagram_account_id = Column(Integer, ForeignKey("instagram_accounts.id"))
    
    # Content Details
    caption_generated = Column(Text)  # The AI generated caption
    caption_final = Column(Text)      # What was actually posted
    hashtags = Column(JSON)           # List of hashtags
    media_url = Column(String)        # URL to the image/video
    media_type = Column(String)       # IMAGE, VIDEO, CAROUSEL
    
    # Planning
    scheduled_time = Column(DateTime)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    
    # Feature 5: Real-time Tracking (Stored as JSON snapshots)
    engagement_snapshots = Column(JSON, default={})
    
    # Feature 6 & 7: Extracting Learnings
    performance_analysis = Column(Text, nullable=True) 
    virality_score = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="content_plans")
    instagram_account = relationship("InstagramAccount", back_populates="content_plans")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
