from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models.trade import Position, Trade
from app.services.trade_service import parse_trades_csv, calculate_net_position

router = APIRouter()

@router.post("/upload", response_model=List[Position])
async def upload_trades(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
    
    content = await file.read()
    try:
        trades = parse_trades_csv(content)
        positions = calculate_net_position(trades)
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/example", response_model=List[Position])
async def get_example_position():
    # Mock data for demonstration
    trades = [
        Trade(trade_id="1", deal_type="Physical", direction="Buy", volume=100000, commodity="Brent", delivery_month="Dec 25", price=75.0),
        Trade(trade_id="2", deal_type="Paper", direction="Sell", volume=50000, commodity="Brent", delivery_month="Dec 25", price=75.5),
        Trade(trade_id="3", deal_type="Paper", direction="Sell", volume=50000, commodity="Brent", delivery_month="Dec 25", price=75.5),
    ]
    return calculate_net_position(trades)

@router.get("/positions", response_model=List[Position])
async def get_positions():
    from app.services.data_manager import data_manager
    from app.services.trade_service import calculate_net_position_from_df
    
    df = data_manager.get_trades()
    if df is None:
        return []
    return calculate_net_position_from_df(df)
