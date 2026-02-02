from fastapi import APIRouter, HTTPException
from typing import List
from app.models.pnl import PnLInput, PnLResult, PnLAttribution
from app.services.pnl_service import calculate_pnl_attribution

router = APIRouter()

@router.post("/calculate", response_model=PnLResult)
async def calculate_pnl(data: PnLInput):
    try:
        # For this endpoint, we are receiving a single PnLInput object.
        # The pnl_engine expects DataFrames for portfolios and curves.
        # This endpoint seems designed for a simple calculator.
        # We should probably expose a new endpoint for the full decomposition 
        # or adapt this one.
        # Given the input model, let's keep the simple service for now 
        # but add a new endpoint for the full engine if needed.
        # Or, we can mock the engine usage here using the input data.
        
        # Let's stick to the existing service for this specific endpoint 
        # as it matches the PnLInput model which is quite simple.
        # But we should add the new decomposition endpoint.
        
        result = calculate_pnl_attribution(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decompose", response_model=List[PnLAttribution])
async def decompose_portfolio_pnl():
    """
    Trigger full portfolio decomposition using loaded data.
    """
    try:
        from app.services.data_manager import data_manager
        from app.core.pnl_engine import decompose_pnl
        
        # In a real scenario, we'd need t0 and t1 data.
        # DataManager currently loads "current" data.
        # We'll simulate t0 data by modifying t1 data slightly.
        
        trades_t1 = data_manager.get_trades()
        curve_t1 = data_manager.get_curve()
        
        if trades_t1 is None or curve_t1 is None:
             raise HTTPException(status_code=400, detail="Data not loaded")

        # Simulate t0 (yesterday)
        trades_t0 = trades_t1.copy()
        # Remove one trade to simulate "New Deal"
        if not trades_t0.empty:
            trades_t0 = trades_t0.iloc[:-1] 
            
        curve_t0 = curve_t1.copy()
        curve_t0['price'] = curve_t0['price'] * 0.99 # 1% price move
        
        attribution_df = decompose_pnl(trades_t0, trades_t1, curve_t0, curve_t1)
        
        return attribution_df.to_dict(orient="records")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attribution", response_model=list[PnLAttribution]) # Use list[PnLAttribution] or List[PnLAttribution]
async def get_pnl_attribution():
    from app.services.data_manager import data_manager
    df = data_manager.get_pnl_attribution()
    if df is None:
        return []
    return df.to_dict(orient="records")
