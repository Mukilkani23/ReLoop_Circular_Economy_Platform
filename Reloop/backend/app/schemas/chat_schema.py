from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserKeyBase(BaseModel):
    public_key: str

class UserKeyCreate(UserKeyBase):
    pass

class UserKeyResponse(UserKeyBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    room_id: str
    encrypted_message: str

class ChatMessageCreate(ChatMessageBase):
    sender_id: int

class ChatMessageResponse(ChatMessageBase):
    id: int
    sender_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatRoomInfo(BaseModel):
    room_id: str
    buyer_id: int
    seller_id: int
    buyer_public_key: Optional[str] = None
    seller_public_key: Optional[str] = None
