from pydantic import BaseModel, Field

class PnLInput(BaseModel):
    yesterday_price: float
    today_price: float
    position_volume: float
    new_deal_volume: float = 0
    new_deal_price: float = 0
    actual_daily_pnl: float = 0  # The "Real" P&L from accounting system

class PnLResult(BaseModel):
    delta_pnl: float
    new_deal_pnl: float
    unexplained_pnl: float
    total_calculated_pnl: float
    total_reported_pnl: float

class PnLAttribution(BaseModel):
    date: str
    driver: str
    pnl_value: float

