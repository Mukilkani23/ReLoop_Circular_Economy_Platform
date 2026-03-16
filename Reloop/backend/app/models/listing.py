"""
WasteListing Model — Represents a waste material listed on the marketplace.
Status: AVAILABLE, RESERVED, SOLD
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class WasteListing(Base):
    __tablename__ = "waste_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    material_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="kg")
    price = Column(Float, nullable=False)
    location = Column(String(150), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="AVAILABLE", index=True)  # AVAILABLE, RESERVED, SOLD
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    owner = relationship("User", back_populates="listings")
    transactions = relationship("Transaction", back_populates="listing")
