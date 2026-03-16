from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.buy_request import BuyRequest
from app.models.user_key import UserKey
from app.models.chat_message import ChatMessage
from app.schemas.chat_schema import UserKeyCreate, UserKeyResponse, ChatMessageResponse, ChatRoomInfo
from app.security.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/keys", response_model=UserKeyResponse)
def upload_public_key(key_data: UserKeyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Upload or update user's public key for E2EE."""
    db_key = db.query(UserKey).filter(UserKey.user_id == current_user.id).first()
    if db_key:
        db_key.public_key = key_data.public_key
    else:
        db_key = UserKey(user_id=current_user.id, public_key=key_data.public_key)
        db.add(db_key)
    
    db.commit()
    db.refresh(db_key)
    return db_key

@router.get("/keys/{user_id}", response_model=UserKeyResponse)
def get_public_key(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user's public key."""
    db_key = db.query(UserKey).filter(UserKey.user_id == user_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="Public key not found for this user")
    return db_key

@router.get("/room/{request_id}", response_model=ChatRoomInfo)
def get_room_info(request_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get chat room info and participant public keys."""
    req = db.query(BuyRequest).filter(BuyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Buy request not found")
    
    if current_user.id not in [req.buyer_id, req.seller_id]:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat room")
    
    buyer_key = db.query(UserKey).filter(UserKey.user_id == req.buyer_id).first()
    seller_key = db.query(UserKey).filter(UserKey.user_id == req.seller_id).first()
    
    return {
        "room_id": f"chat_{request_id}",
        "buyer_id": req.buyer_id,
        "seller_id": req.seller_id,
        "buyer_public_key": buyer_key.public_key if buyer_key else None,
        "seller_public_key": seller_key.public_key if seller_key else None
    }

@router.get("/messages/{room_id}", response_model=List[ChatMessageResponse])
def get_chat_messages(room_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve encrypted message history for a room."""
    # Basic room permission check
    if room_id.startswith("chat_"):
        request_id = int(room_id.replace("chat_", ""))
        req = db.query(BuyRequest).filter(BuyRequest.id == request_id).first()
        if not req or current_user.id not in [req.buyer_id, req.seller_id]:
            raise HTTPException(status_code=403, detail="Unauthorized")
    
    messages = db.query(ChatMessage).filter(ChatMessage.room_id == room_id).order_by(ChatMessage.timestamp.asc()).all()
    return messages
