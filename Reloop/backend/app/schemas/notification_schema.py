"""
Notification Pydantic Schemas — Validation for notifications.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    message: str
    listing_id: Optional[int] = None
    buyer_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
