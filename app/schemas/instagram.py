from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ScheduleMode(str, Enum):
    NOW = "now"
    MANUAL = "manual"
    AUTO_AI = "auto"

class PostSchedule(BaseModel):
    image_url: str
    caption_final: str
    mode: ScheduleMode = ScheduleMode.NOW
    manual_hours_delay: int = 0
    
    # NEW FIELDS TO BE SAVED
    caption_generated: Optional[str] = None # The best AI option selected by user
    media_type: Optional[str] = None # IMAGE, VIDEO, etc.
    hashtags: Optional[List[str]] = None
