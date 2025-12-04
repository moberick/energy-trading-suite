from fastapi import APIRouter, HTTPException
from app.models.arb import ArbInput, ArbResult
from app.services.arb_service import calculate_arb

router = APIRouter()

@router.post("/calculate", response_model=ArbResult)
async def calculate(data: ArbInput):
    try:
        return calculate_arb(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
