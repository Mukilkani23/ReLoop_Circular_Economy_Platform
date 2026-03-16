"""
Analytics Service — Environmental impact calculations.
"""

# Emission factors: kg CO2 saved per kg of material recycled
EMISSION_FACTORS = {
    "steel": 1.8,
    "metal": 1.8,
    "iron": 1.8,
    "aluminum": 9.0,
    "plastic": 2.5,
    "paper": 1.2,
    "cardboard": 1.2,
    "glass": 0.6,
    "wood": 0.9,
    "textile": 3.0,
    "rubber": 1.5,
    "food": 0.5,
    "organic": 0.5,
    "electronic": 5.0,
    "chemical": 2.0,
    "copper": 3.5,
}

# Energy factors: kWh saved per kg of material recycled
ENERGY_FACTORS = {
    "steel": 1.3,
    "metal": 1.3,
    "iron": 1.3,
    "aluminum": 14.0,
    "plastic": 5.8,
    "paper": 4.1,
    "cardboard": 4.1,
    "glass": 0.3,
    "wood": 0.5,
    "textile": 2.5,
    "rubber": 1.0,
    "food": 0.3,
    "organic": 0.3,
    "electronic": 8.0,
    "chemical": 1.5,
    "copper": 6.0,
}


def get_emission_factor(material_type: str) -> float:
    """Get CO2 emission factor for a material type."""
    material_lower = material_type.lower()
    for key, factor in EMISSION_FACTORS.items():
        if key in material_lower:
            return factor
    return 1.0  # Default factor


def get_energy_factor(material_type: str) -> float:
    """Get energy saving factor for a material type."""
    material_lower = material_type.lower()
    for key, factor in ENERGY_FACTORS.items():
        if key in material_lower:
            return factor
    return 0.5  # Default factor


def calculate_impact(material_type: str, quantity_kg: float) -> dict:
    """Calculate environmental impact of recycling a given material."""
    co2_saved = quantity_kg * get_emission_factor(material_type)
    energy_saved = quantity_kg * get_energy_factor(material_type)
    landfill_avoided = quantity_kg / 1000  # rough estimate in tons

    return {
        "co2_saved_kg": round(co2_saved, 2),
        "energy_saved_kwh": round(energy_saved, 2),
        "landfill_avoided_tons": round(landfill_avoided, 3),
    }
