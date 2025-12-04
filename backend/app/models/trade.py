from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import date

class Trade(BaseModel):
    trade_id: str
    deal_type: Literal['Physical', 'Paper']
    direction: Literal['Buy', 'Sell']
    volume: float
    commodity: str
    delivery_month: str  # Format: "Dec 25" or "2025-12"
    price: float
    counterparty: Optional[str] = None

class Position(BaseModel):
    commodity: str
    delivery_month: str
    net_volume: float
    exposure_status: str  # "Long", "Short", "Flat"
