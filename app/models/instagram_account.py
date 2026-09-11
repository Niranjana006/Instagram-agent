from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from influencer_agent.app.db.base import Base

class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Instagram Info
    instagram_id = Column(String, unique=True, index=True)  # The 178... number
    username = Column(String)
    access_token = Column(String)  # Long-lived token
    
    owner = relationship("User", back_populates="instagram_accounts")
    content_plans = relationship("ContentPlan", back_populates="instagram_account")
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
