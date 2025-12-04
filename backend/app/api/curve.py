from fastapi import APIRouter, HTTPException
from typing import List
from app.models.curve import CurvePoint, ValidationResult, AuditLog
from app.services.curve_service import validate_curve, get_audit_logs, add_audit_log

router = APIRouter()

@router.post("/validate", response_model=ValidationResult)
async def validate(curve: List[CurvePoint]):
    try:
        # Log the validation attempt (simulating a "Save" or "Check" action)
        add_audit_log("Trader1", "Validate Curve", f"Validated {len(curve)} points")
        return validate_curve(curve)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-logs", response_model=List[AuditLog])
async def get_logs():
    return get_audit_logs()
