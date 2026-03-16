"""
Notification Model — Tracks notifications for users.
Types: BUY_REQUEST, REQUEST_ACCEPTED, REQUEST_REJECTED, MESSAGE_RECEIVED
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    listing_id = Column(Integer, ForeignKey("waste_listings.id"), nullable=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
