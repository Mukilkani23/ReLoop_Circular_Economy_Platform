"""
Requests API Router — CRUD and actions (Accept/Reject) for Buy Requests.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.listing import WasteListing
from app.models.buy_request import BuyRequest
from app.models.notification import Notification
from app.schemas.buy_request_schema import BuyRequestCreate
from app.security.auth import get_current_user

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_request(
    request_data: BuyRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new Buy Request."""
    listing = db.query(WasteListing).filter(WasteListing.id == request_data.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Security Rule: Identify self-request
    if listing.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot request your own listing")

    if listing.status != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Listing is no longer available")

    # Security Rule: Prevent duplicate pending requests
    existing = db.query(BuyRequest).filter(
        BuyRequest.listing_id == request_data.listing_id,
        BuyRequest.buyer_id == current_user.id,
        BuyRequest.status == "PENDING"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already have a pending request for this listing")

    # Create Request
    new_request = BuyRequest(
        listing_id=listing.id,
        seller_id=listing.user_id,
        buyer_id=current_user.id,
        status="PENDING"
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # Create Notification for Seller
    notification = Notification(
        user_id=listing.user_id,
        type="BUY_REQUEST",
        message=f"{current_user.email} has requested to buy: {listing.title}",
        listing_id=listing.id,
        buyer_id=current_user.id
    )
    db.add(notification)
    db.commit()

    return {
        "message": "Your request has been sent to the seller. They can contact you through chat.",
        "request_id": new_request.id
    }


@router.get("/seller")
def get_seller_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all requests sent to the current user's listings."""
    requests = db.query(BuyRequest).filter(BuyRequest.seller_id == current_user.id).order_by(BuyRequest.created_at.desc()).all()
    results = []
    for req in requests:
        listing = db.query(WasteListing).filter(WasteListing.id == req.listing_id).first()
        buyer = db.query(User).filter(User.id == req.buyer_id).first()
        results.append({
            "id": req.id,
            "listing_id": req.listing_id,
            "listing_title": listing.title if listing else "Unknown",
            "quantity": listing.quantity if listing else 0,
            "unit": listing.unit if listing else "",
            "buyer_id": req.buyer_id,
            "buyer_email": buyer.email if buyer else "Unknown",
            "status": req.status,
            "created_at": req.created_at
        })
    return results


@router.get("/buyer")
def get_buyer_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all requests initiated by the current user."""
    requests = db.query(BuyRequest).filter(BuyRequest.buyer_id == current_user.id).order_by(BuyRequest.created_at.desc()).all()
    results = []
    for req in requests:
        listing = db.query(WasteListing).filter(WasteListing.id == req.listing_id).first()
        seller = db.query(User).filter(User.id == req.seller_id).first()
        results.append({
            "id": req.id,
            "listing_id": req.listing_id,
            "listing_title": listing.title if listing else "Unknown",
            "seller_id": req.seller_id,
            "seller_email": seller.email if seller else "Unknown",
            "status": req.status,
            "created_at": req.created_at
        })
    return results


@router.post("/{request_id}/accept")
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a buy request. Reserves the listing and rejects others."""
    req = db.query(BuyRequest).filter(BuyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")
    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request is already {req.status}")

    listing = db.query(WasteListing).filter(WasteListing.id == req.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Listing is no longer available")

    # 1. Accept this request
    req.status = "ACCEPTED"
    
    # 2. Reserve Listing
    listing.status = "RESERVED"

    # 3. Reject other pending requests for this listing
    other_requests = db.query(BuyRequest).filter(
        BuyRequest.listing_id == listing.id,
        BuyRequest.id != request_id,
        BuyRequest.status == "PENDING"
    ).all()
    
    for other_req in other_requests:
        other_req.status = "REJECTED"
        # Notify rejected buyers
        rej_notif = Notification(
            user_id=other_req.buyer_id,
            type="REQUEST_REJECTED",
            message=f"Your request for '{listing.title}' was rejected because it was sold to someone else.",
            listing_id=listing.id
        )
        db.add(rej_notif)

    # 4. Notify accepted buyer
    acc_notif = Notification(
        user_id=req.buyer_id,
        type="REQUEST_ACCEPTED",
        message=f"Your request for '{listing.title}' was accepted! Check your chats.",
        listing_id=listing.id,
        buyer_id=req.buyer_id
    )
    db.add(acc_notif)
    
    db.commit()
    return {"message": "Request accepted and listing reserved"}


@router.post("/{request_id}/reject")
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a buy request."""
    req = db.query(BuyRequest).filter(BuyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")
    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request is already {req.status}")

    req.status = "REJECTED"

    listing = db.query(WasteListing).filter(WasteListing.id == req.listing_id).first()
    listing_title = listing.title if listing else "Unknown"

    # Notify buyer
    notif = Notification(
        user_id=req.buyer_id,
        type="REQUEST_REJECTED",
        message=f"Your request for '{listing_title}' was rejected.",
        listing_id=req.listing_id
    )
    db.add(notif)
    db.commit()

    return {"message": "Request rejected"}
@router.post("/{request_id}/complete")
def complete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a transaction as completed (Buyer only)."""
    req = db.query(BuyRequest).filter(BuyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the buyer can complete the transaction")
    if req.status != "ACCEPTED":
        raise HTTPException(status_code=400, detail="Transaction can only be completed after being accepted")

    req.status = "COMPLETED"
    
    listing = db.query(WasteListing).filter(WasteListing.id == req.listing_id).first()
    if listing:
        listing.status = "SOLD"

    # Notify seller
    notif = Notification(
        user_id=req.seller_id,
        type="TRANSACTION_COMPLETED",
        message=f"Transaction for '{listing.title if listing else 'material'}' has been marked as completed by the buyer.",
        listing_id=req.listing_id
    )
    db.add(notif)
    db.commit()

    return {"message": "Transaction completed successfully!"}
