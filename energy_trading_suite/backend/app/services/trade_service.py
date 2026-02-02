import pandas as pd
from typing import List, BinaryIO
from app.models.trade import Trade, Position
import io

def parse_trades_csv(file_content: bytes) -> List[Trade]:
    df = pd.read_csv(io.BytesIO(file_content))
    trades = []
    for _, row in df.iterrows():
        trade = Trade(
            trade_id=str(row['trade_id']),
            deal_type=row['deal_type'],
            direction=row['direction'],
            volume=float(row['volume']),
            commodity=row['commodity'],
            delivery_month=row['delivery_month'],
            price=float(row['price']),
            counterparty=row.get('counterparty')
        )
        trades.append(trade)
    return trades

def calculate_net_position(trades: List[Trade]) -> List[Position]:
    if not trades:
        return []
    # Convert to DataFrame for easier aggregation
    data = [t.dict() for t in trades]
    df = pd.DataFrame(data)
    return calculate_net_position_from_df(df)

def calculate_net_position_from_df(df: pd.DataFrame) -> List[Position]:
    if df.empty:
        return []

    # Adjust volume based on direction
    df['signed_volume'] = df.apply(
        lambda x: x['volume'] if x['direction'] == 'Buy' else -x['volume'], axis=1
    )

    # Group by Commodity and Delivery Month
    grouped = df.groupby(['commodity', 'delivery_month'])['signed_volume'].sum().reset_index()

    positions = []
    for _, row in grouped.iterrows():
        net_vol = row['signed_volume']
        status = "Flat"
        if net_vol > 0:
            status = "Long"
        elif net_vol < 0:
            status = "Short"
        
        positions.append(Position(
            commodity=row['commodity'],
            delivery_month=row['delivery_month'],
            net_volume=net_vol,
            exposure_status=status
        ))
    
    return positions
