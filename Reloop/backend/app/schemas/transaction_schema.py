"""
Transaction Pydantic Schemas — Request/response validation for transaction endpoints.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransactionCreate(BaseModel):
    listing_id: int


class TransactionResponse(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class BuyResponse(BaseModel):
    message: str
    transaction_id: int
