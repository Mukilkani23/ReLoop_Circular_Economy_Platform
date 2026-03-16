"""
Marketplace API Router — CRUD for waste listings + search + buy action.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.listing import WasteListing
from app.models.transaction import Transaction
from app.models.buy_request import BuyRequest
from app.schemas.listing_schema import ListingCreate, ListingUpdate, ListingResponse
from app.schemas.transaction_schema import TransactionResponse, BuyResponse
from app.schemas.buy_request_schema import BuyRequestCreate
from app.security.auth import get_current_user
from app.services.email_service import send_buyer_notification

router = APIRouter(prefix="/listings", tags=["Marketplace"])


@router.post("/", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    listing_data: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new waste listing."""
    new_listing = WasteListing(
        title=listing_data.title,
        material_type=listing_data.material_type,
        description=listing_data.description,
        quantity=listing_data.quantity,
        unit=listing_data.unit,
        price=listing_data.price,
        location=listing_data.location,
        user_id=current_user.id,
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return ListingResponse(
        **{c.name: getattr(new_listing, c.name) for c in new_listing.__table__.columns},
        owner_name=current_user.username,
    )


@router.get("/", response_model=List[ListingResponse])
def get_all_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Browse all waste listings (paginated)."""
    listings = db.query(WasteListing).order_by(WasteListing.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for listing in listings:
        owner = db.query(User).filter(User.id == listing.user_id).first()
        results.append(
            ListingResponse(
                **{c.name: getattr(listing, c.name) for c in listing.__table__.columns},
                owner_name=owner.username if owner else None,
            )
        )
    return results


@router.get("/search", response_model=List[ListingResponse])
def search_listings(
    material: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Search listings by material type and/or location."""
    query = db.query(WasteListing).filter(WasteListing.status == "AVAILABLE")
    if material:
        query = query.filter(WasteListing.material_type.ilike(f"%{material}%"))
    if location:
        query = query.filter(WasteListing.location.ilike(f"%{location}%"))
    listings = query.order_by(WasteListing.created_at.desc()).all()
    results = []
    for listing in listings:
        owner = db.query(User).filter(User.id == listing.user_id).first()
        results.append(
            ListingResponse(
                **{c.name: getattr(listing, c.name) for c in listing.__table__.columns},
                owner_name=owner.username if owner else None,
            )
        )
    return results


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get a single listing by ID."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    owner = db.query(User).filter(User.id == listing.user_id).first()
    return ListingResponse(
        **{c.name: getattr(listing, c.name) for c in listing.__table__.columns},
        owner_name=owner.username if owner else None,
    )


@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int,
    listing_data: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a listing (owner only)."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")

    update_data = listing_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(listing, key, value)
    db.commit()
    db.refresh(listing)
    return ListingResponse(
        **{c.name: getattr(listing, c.name) for c in listing.__table__.columns},
        owner_name=current_user.username,
    )


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a listing (owner only)."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    db.delete(listing)
    db.commit()


@router.post("/{listing_id}/buy", response_model=BuyResponse)
def buy_listing(
    listing_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Initiate a purchase transaction for a listing (thread-safe status check)."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot buy your own listing")
    if listing.status != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Listing is no longer available")

    # Reserve the listing
    listing.status = "RESERVED"
    transaction = Transaction(
        listing_id=listing_id,
        buyer_id=current_user.id,
        status="PENDING",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    owner = db.query(User).filter(User.id == listing.user_id).first()
    if owner and owner.email:
        background_tasks.add_task(
            send_buyer_notification,
            seller_email=owner.email,
            listing_title=listing.title,
            listing_quantity=listing.quantity,
            listing_unit=listing.unit,
            buyer_company=current_user.company_name or "N/A",
            buyer_email=current_user.email
        )

    return {
        "message": "Purchase request sent successfully. Seller has been notified.",
        "transaction_id": transaction.id
    }


@router.post("/{listing_id}/request")
def request_material(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a buy request for a listing."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot request your own listing")

    # Check if request already exists
    existing = db.query(BuyRequest).filter(
        BuyRequest.listing_id == listing_id,
        BuyRequest.buyer_id == current_user.id
    ).first()
    if existing:
        return {"message": "Request already sent", "id": existing.id}

    new_request = BuyRequest(
        listing_id=listing_id,
        seller_id=listing.user_id,
        buyer_id=current_user.id,
        status="PENDING"
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "message": "Your request has been sent to the seller. They can contact you through chat.",
        "request_id": new_request.id
    }
