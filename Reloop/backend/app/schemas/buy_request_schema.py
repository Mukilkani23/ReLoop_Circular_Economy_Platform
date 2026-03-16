"""
BuyRequest Pydantic Schemas — Validation for request creation and notification responses.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BuyRequestCreate(BaseModel):
    listing_id: int


class NotificationResponse(BaseModel):
    id: int
    listing_title: str
    quantity: float
    unit: str
    buyer_email: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
