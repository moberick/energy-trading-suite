from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.core.arb_engine import LNGCargo
from app.models.arb import ArbInput, ArbResult # Keep this if calculate endpoint is retained
from app.services.arb_service import calculate_arb # Keep this if calculate endpoint is retained

router = APIRouter()

@router.post("/calculate", response_model=ArbResult)
async def calculate(data: ArbInput):
    try:
        return calculate_arb(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimize", response_model=Dict[str, Any])
async def optimize_lng_route(fob_location: str = "USGC"):
    try:
        cargo = LNGCargo()
        
        # Mock Destinations
        destinations = {
            "JKM (Asia)": {"price": 14.50, "distance": 9500}, 
            "TTF (Europe)": {"price": 12.20, "distance": 4000},
            "NBP (UK)": {"price": 12.15, "distance": 4100}
        }
        
        results = cargo.optimize_route(fob_location, destinations)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

