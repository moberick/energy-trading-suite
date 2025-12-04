from app.models.pnl import PnLInput, PnLResult

def calculate_pnl_attribution(data: PnLInput) -> PnLResult:
    # 1. Delta P&L (Price Movement on existing position)
    # Formula: Q * (Pt - Pt-1)
    delta_pnl = data.position_volume * (data.today_price - data.yesterday_price)

    # 2. New Deal P&L (Value capture on new trades)
    # Formula: NewVolume * (Pt - DealPrice)
    new_deal_pnl = 0
    if data.new_deal_volume != 0:
        new_deal_pnl = data.new_deal_volume * (data.today_price - data.new_deal_price)

    # Total Calculated
    total_calculated = delta_pnl + new_deal_pnl

    # 3. Unexplained P&L (Residual)
    # If actual_daily_pnl is provided, calculate the difference
    # Otherwise assume perfect attribution (Unexplained = 0)
    unexplained = 0
    total_reported = total_calculated
    
    if data.actual_daily_pnl != 0:
        total_reported = data.actual_daily_pnl
        unexplained = total_reported - total_calculated

    return PnLResult(
        delta_pnl=round(delta_pnl, 2),
        new_deal_pnl=round(new_deal_pnl, 2),
        unexplained_pnl=round(unexplained, 2),
        total_calculated_pnl=round(total_calculated, 2),
        total_reported_pnl=round(total_reported, 2)
    )
