"""
Recommendation Service — Bridges AI engine inference to the backend API.
"""
import sys
import os

# Add the project root to the path so we can import from ai-engine
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

try:
    from importlib import import_module
    predict_module = import_module("ai-engine.inference.predict")
    get_recommendations = predict_module.get_recommendations
    AI_ENGINE_AVAILABLE = True
except Exception:
    AI_ENGINE_AVAILABLE = False

    # Fallback: keyword-based recommendations
    FALLBACK_RECOMMENDATIONS = {
        "plastic": [
            {"industry": "Plastic Recycling Plant", "match_score": 0.92, "description": "Processes post-consumer and industrial plastic waste into reusable pellets and raw materials."},
            {"industry": "Packaging Industry", "match_score": 0.85, "description": "Uses recycled plastic for sustainable packaging solutions."},
            {"industry": "Textile Manufacturing", "match_score": 0.71, "description": "Converts PET plastic into polyester fibers for clothing and textiles."},
        ],
        "metal": [
            {"industry": "Steel Recycling Plant", "match_score": 0.95, "description": "Melts and refines scrap metal into new steel products."},
            {"industry": "Metal Foundry", "match_score": 0.88, "description": "Casts recycled metals into industrial components and parts."},
            {"industry": "Construction Industry", "match_score": 0.76, "description": "Uses recycled metal in structural reinforcement and building materials."},
        ],
        "wood": [
            {"industry": "Biomass Power Plant", "match_score": 0.90, "description": "Converts wood waste into renewable energy through combustion."},
            {"industry": "Furniture Manufacturing", "match_score": 0.82, "description": "Repurposes salvaged wood into new furniture and home goods."},
            {"industry": "Paper Mill", "match_score": 0.74, "description": "Processes wood chips into paper and cardboard products."},
        ],
        "textile": [
            {"industry": "Insulation Manufacturing", "match_score": 0.88, "description": "Shreds textile waste into thermal and acoustic insulation materials."},
            {"industry": "Second-hand Retail", "match_score": 0.80, "description": "Sorts and resells usable textiles to reduce fashion waste."},
            {"industry": "Cleaning Supply Industry", "match_score": 0.68, "description": "Converts textile scraps into industrial cleaning rags and wipes."},
        ],
        "food": [
            {"industry": "Biogas Plant", "match_score": 0.93, "description": "Converts organic waste into methane-based renewable energy via anaerobic digestion."},
            {"industry": "Composting Facility", "match_score": 0.87, "description": "Transforms food waste into nutrient-rich compost for agriculture."},
            {"industry": "Animal Feed Production", "match_score": 0.72, "description": "Processes suitable food waste into animal feed supplements."},
        ],
        "glass": [
            {"industry": "Glass Manufacturing", "match_score": 0.94, "description": "Melts cullet (crushed glass) into new glass containers and products."},
            {"industry": "Construction Industry", "match_score": 0.78, "description": "Uses crushed glass as aggregate in concrete and road base."},
            {"industry": "Fiberglass Production", "match_score": 0.70, "description": "Converts recycled glass into fiberglass insulation and composites."},
        ],
        "paper": [
            {"industry": "Paper Mill", "match_score": 0.91, "description": "Repulps waste paper into new paper and cardboard products."},
            {"industry": "Packaging Industry", "match_score": 0.84, "description": "Creates eco-friendly packaging from recycled paper fibers."},
            {"industry": "Insulation Manufacturing", "match_score": 0.69, "description": "Processes shredded paper into cellulose insulation for buildings."},
        ],
        "electronic": [
            {"industry": "E-waste Recycling", "match_score": 0.93, "description": "Safely dismantles electronics to recover reusable components and materials."},
            {"industry": "Precious Metal Recovery", "match_score": 0.86, "description": "Extracts gold, silver, and platinum from circuit boards and connectors."},
            {"industry": "Refurbished Electronics", "match_score": 0.75, "description": "Repairs and resells functional electronics, extending product lifespans."},
        ],
        "rubber": [
            {"industry": "Tire Recycling Plant", "match_score": 0.91, "description": "Shreds tires into crumb rubber for various applications."},
            {"industry": "Asphalt Production", "match_score": 0.83, "description": "Mixes crumb rubber into asphalt for durable, noise-reducing roads."},
            {"industry": "Pyrolysis Plant", "match_score": 0.74, "description": "Converts rubber waste into fuel oil, carbon black, and steel through thermal decomposition."},
        ],
        "chemical": [
            {"industry": "Chemical Recycling Plant", "match_score": 0.89, "description": "Purifies and reprocesses chemical waste into usable industrial chemicals."},
            {"industry": "Solvent Recovery Facility", "match_score": 0.82, "description": "Distills and reclaims used solvents for reuse in manufacturing."},
            {"industry": "Waste Treatment Facility", "match_score": 0.73, "description": "Safely neutralizes and processes hazardous chemical waste."},
        ],
    }

    def get_recommendations(waste_description: str, top_n: int = 3):
        """Fallback keyword-based recommendations when AI model is not available."""
        desc_lower = waste_description.lower()
        for keyword, recs in FALLBACK_RECOMMENDATIONS.items():
            if keyword in desc_lower:
                return recs[:top_n]
        # Generic recommendations
        return [
            {"industry": "General Recycling Facility", "match_score": 0.60, "description": "Handles mixed waste streams for sorting and recycling."},
            {"industry": "Waste-to-Energy Plant", "match_score": 0.55, "description": "Converts non-recyclable waste into electricity and heat."},
            {"industry": "Industrial Waste Management", "match_score": 0.50, "description": "Provides comprehensive waste management solutions for businesses."},
        ]
