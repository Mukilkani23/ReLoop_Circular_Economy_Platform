"""
BuyRequest Model — Tracks requests from buyers for specific waste listings.
Status: PENDING, ACCEPTED, REJECTED
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class BuyRequest(Base):
    __tablename__ = "buy_requests"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("waste_listings.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, ACCEPTED, REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    listing = relationship("WasteListing")
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])
