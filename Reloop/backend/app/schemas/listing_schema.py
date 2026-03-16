"""
Listing Pydantic Schemas — Request/response validation for marketplace endpoints.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ListingCreate(BaseModel):
    title: str
    material_type: str
    description: Optional[str] = None
    quantity: float
    unit: str = "kg"
    price: float
    location: str


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    material_type: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    status: Optional[str] = None


class ListingResponse(BaseModel):
    id: int
    title: str
    material_type: str
    description: Optional[str] = None
    quantity: float
    unit: str
    price: float
    location: str
    status: str
    user_id: int
    owner_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    industry: str
    match_score: float
    description: str
