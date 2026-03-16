from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class UserKey(Base):
    __tablename__ = "user_keys"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    public_key = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
