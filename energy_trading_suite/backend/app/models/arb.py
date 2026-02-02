from pydantic import BaseModel

class ArbInput(BaseModel):
    sales_price: float  # DES
    purchase_price: float  # FOB
    freight_rate: float  # Daily Hire Rate ($/day)
    distance: float  # Nautical Miles
    speed: float  # Knots (Slow Steaming parameter)
    fuel_consumption: float  # Tons/day at given speed
    fuel_price: float  # $/ton
    insurance_cost: float  # $/bbl
    volume: float  # bbls (e.g. 2,000,000 for VLCC)

class ArbResult(BaseModel):
    freight_cost_per_bbl: float
    total_logistics_cost: float
    margin: float
    is_open: bool
    voyage_days: float
