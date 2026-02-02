from typing import List
from app.models.curve import CurvePoint, ValidationAlert, ValidationResult, AuditLog
from datetime import datetime

# In-memory storage for audit logs
AUDIT_LOGS = []

def add_audit_log(user: str, action: str, details: str):
    log = AuditLog(
        timestamp=datetime.now(),
        user=user,
        action=action,
        details=details
    )
    AUDIT_LOGS.append(log)
    return log

def get_audit_logs() -> List[AuditLog]:
    return sorted(AUDIT_LOGS, key=lambda x: x.timestamp, reverse=True)

def validate_curve(curve: List[CurvePoint]) -> ValidationResult:
    alerts = []
    
    # Sort curve by month logic would be needed for real dates, 
    # but assuming input is sorted for this mock.
    
    for i, point in enumerate(curve):
        # 1. Stale Check
        if point.price == point.yesterday_price:
            alerts.append(ValidationAlert(
                month=point.month,
                check_type="Stale",
                message=f"Price {point.price} unchanged from yesterday.",
                severity="Medium"
            ))
        
        # 2. Fly Check (Butterfly Spread)
        # Needs prev and next points
        if i > 0 and i < len(curve) - 1:
            prev_point = curve[i-1]
            next_point = curve[i+1]
            
            # Simple average check
            avg_price = (prev_point.price + next_point.price) / 2
            diff = abs(point.price - avg_price)
            
            # Seasonality Logic: Higher threshold for Winter months
            threshold = 0.5
            if any(m in point.month for m in ["Dec", "Jan", "Feb"]):
                threshold = 1.0  # Higher tolerance in winter
            
            if diff > threshold:
                alerts.append(ValidationAlert(
                    month=point.month,
                    check_type="Fly",
                    message=f"Price {point.price} deviates from spread avg {avg_price:.2f} by {diff:.2f} (Threshold: {threshold}).",
                    severity="High"
                ))

    return ValidationResult(
        alerts=alerts,
        is_valid=len(alerts) == 0
    )
