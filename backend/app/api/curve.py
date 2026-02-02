from fastapi import APIRouter, HTTPException
from typing import List
from app.models.curve import CurvePoint, ValidationResult, AuditLog
from app.services.curve_service import validate_curve, get_audit_logs, add_audit_log

router = APIRouter()

@router.post("/validate", response_model=ValidationResult)
async def validate(curve_points: List[CurvePoint]):
    try:
        # Convert Pydantic models to DataFrame
        data = [{"tenor": p.tenor, "price": p.price, "last_update": datetime.now()} for p in curve_points]
        df = pd.DataFrame(data)
        
        # Initialize Engine
        from app.core.curve_engine import ForwardCurve
        engine = ForwardCurve(df)
        
        # Run Validation
        alerts_dict = engine.validate_integrity()
        
        # Convert alerts to response model
        validation_alerts = []
        for check_type, messages in alerts_dict.items():
            for msg in messages:
                validation_alerts.append(ValidationAlert(
                    month=curve_points[0].tenor if curve_points else "N/A", # Message contains tenor
                    check_type=check_type,
                    message=msg,
                    severity="High"
                ))
        
        is_valid = len(validation_alerts) == 0
        
        # Log the validation attempt
        add_audit_log("Trader1", "Validate Curve", f"Validated {len(curve_points)} points. Valid: {is_valid}")
        
        return ValidationResult(alerts=validation_alerts, is_valid=is_valid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-logs", response_model=List[AuditLog])
async def get_logs():
    return get_audit_logs()

@router.get("/", response_model=List[CurvePoint])
async def get_curve():
    from app.services.data_manager import data_manager
    df = data_manager.get_curve()
    if df is None:
        return []
    return df.to_dict(orient="records")
