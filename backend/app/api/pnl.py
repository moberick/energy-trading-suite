from fastapi import APIRouter, HTTPException
from app.models.pnl import PnLInput, PnLResult
from app.services.pnl_service import calculate_pnl_attribution

router = APIRouter()

@router.post("/calculate", response_model=PnLResult)
async def calculate_pnl(data: PnLInput):
    try:
        result = calculate_pnl_attribution(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
