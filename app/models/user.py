from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from influencer_agent.app.db.base import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    
    # Relationships
    instagram_accounts = relationship("InstagramAccount", back_populates="owner")
    content_plans = relationship("ContentPlan", back_populates="user")
    
    created_at = Column(DateTime, default=datetime.utcnow)
