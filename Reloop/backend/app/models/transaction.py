"""
Transaction Model — Tracks purchases of waste listings.
Status: PENDING, COMPLETED, CANCELLED
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("waste_listings.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, COMPLETED, CANCELLED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    listing = relationship("WasteListing", back_populates="transactions")
    buyer = relationship("User", back_populates="transactions")
