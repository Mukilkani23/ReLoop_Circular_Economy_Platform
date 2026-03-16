"""
Analytics API Router — Environmental impact statistics and platform metrics.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.listing import WasteListing
from app.models.transaction import Transaction
from app.services.analytics_service import calculate_impact

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/impact")
def get_impact_analytics(db: Session = Depends(get_db)):
    """Get platform-wide environmental impact statistics."""
    # Get all sold/reserved listings for impact calculation
    active_listings = db.query(WasteListing).filter(
        WasteListing.status.in_(["RESERVED", "SOLD"])
    ).all()

    total_waste_diverted = 0.0
    total_co2_saved = 0.0
    total_energy_saved = 0.0
    total_landfill_avoided = 0.0

    for listing in active_listings:
        impact = calculate_impact(listing.material_type, listing.quantity)
        total_waste_diverted += listing.quantity
        total_co2_saved += impact["co2_saved_kg"]
        total_energy_saved += impact["energy_saved_kwh"]
        total_landfill_avoided += impact["landfill_avoided_tons"]

    # Platform metrics
    total_listings = db.query(func.count(WasteListing.id)).scalar() or 0
    available_listings = db.query(func.count(WasteListing.id)).filter(
        WasteListing.status == "AVAILABLE"
    ).scalar() or 0
    total_transactions = db.query(func.count(Transaction.id)).scalar() or 0

    return {
        "environmental_impact": {
            "waste_diverted_kg": round(total_waste_diverted, 2),
            "co2_saved_kg": round(total_co2_saved, 2),
            "energy_saved_kwh": round(total_energy_saved, 2),
            "landfill_avoided_tons": round(total_landfill_avoided, 3),
        },
        "platform_metrics": {
            "total_listings": total_listings,
            "available_listings": available_listings,
            "total_transactions": total_transactions,
        },
    }
