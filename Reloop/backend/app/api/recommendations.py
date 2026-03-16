"""
Recommendations API Router — AI-powered waste-to-industry matchmaking.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.listing import WasteListing
from app.schemas.listing_schema import RecommendationResponse
from app.services.recommendation_service import get_recommendations
from app.services.analytics_service import calculate_impact

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])


@router.get("/{listing_id}", response_model=List[RecommendationResponse])
def get_listing_recommendations(listing_id: int, db: Session = Depends(get_db)):
    """Get AI-powered industry recommendations for a waste listing."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Build description from listing data
    description = f"{listing.material_type} {listing.title}"
    if listing.description:
        description += f" {listing.description}"

    recommendations = get_recommendations(description, top_n=3)
    return recommendations


@router.get("/material/{material_type}", response_model=List[RecommendationResponse])
def get_material_recommendations(material_type: str):
    """Get AI-powered industry recommendations for a given material type (no listing required)."""
    recommendations = get_recommendations(material_type, top_n=3)
    return recommendations


@router.get("/impact/{listing_id}")
def get_listing_impact(listing_id: int, db: Session = Depends(get_db)):
    """Get environmental impact score for a specific listing."""
    listing = db.query(WasteListing).filter(WasteListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    impact = calculate_impact(listing.material_type, listing.quantity)
    return {
        "listing_id": listing.id,
        "material_type": listing.material_type,
        "quantity_kg": listing.quantity,
        **impact,
    }
