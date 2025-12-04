from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CurvePoint(BaseModel):
    month: str  # "Jan 26"
    price: float
    yesterday_price: float

class ValidationAlert(BaseModel):
    month: str
    check_type: str  # "Stale", "Fly"
    message: str
    severity: str  # "High", "Medium", "Low"

class ValidationResult(BaseModel):
    alerts: List[ValidationAlert]
    is_valid: bool

class AuditLog(BaseModel):
    timestamp: datetime
    user: str
    action: str
    details: str
