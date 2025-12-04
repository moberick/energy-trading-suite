from app.models.arb import ArbInput, ArbResult

def calculate_arb(data: ArbInput) -> ArbResult:
    # 1. Calculate Voyage Time
    # Distance (nm) / Speed (knots) / 24 hours = Days
    voyage_days = data.distance / data.speed / 24
    
    # Add port days (loading/discharging) - assumption: 5 days total
    total_days = voyage_days + 5
    
    # 2. Calculate Freight Cost (Total)
    # (Days * Hire Rate) + (Days * Fuel Cons * Fuel Price)
    # Note: Fuel consumption is usually only for sea days, port consumption is lower.
    # For simplicity, we'll use sea days for fuel + 5 days port fuel (assumed lower or included).
    # Let's stick to the prompt's simplicity but add the speed factor.
    
    charter_cost = total_days * data.freight_rate
    fuel_cost = voyage_days * data.fuel_consumption * data.fuel_price
    
    total_shipping_cost = charter_cost + fuel_cost
    
    # 3. Freight Cost per Barrel
    freight_per_bbl = total_shipping_cost / data.volume
    
    # 4. Margin
    # Sales Price - Purchase Price - Freight - Insurance
    margin = data.sales_price - data.purchase_price - freight_per_bbl - data.insurance_cost
    
    return ArbResult(
        freight_cost_per_bbl=round(freight_per_bbl, 2),
        total_logistics_cost=round(freight_per_bbl + data.insurance_cost, 2),
        margin=round(margin, 2),
        is_open=margin > 0,
        voyage_days=round(voyage_days, 1)
    )
