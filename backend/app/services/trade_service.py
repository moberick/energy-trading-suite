import pandas as pd
from typing import List, BinaryIO
from app.models.trade import Trade, Position
import io

def parse_trades_csv(file_content: bytes) -> List[Trade]:
    df = pd.read_csv(io.BytesIO(file_content))
    trades = []
    for _, row in df.iterrows():
        trade = Trade(
            trade_id=str(row['Trade ID']),
            deal_type=row['Deal Type'],
            direction=row['Direction'],
            volume=float(row['Volume']),
            commodity=row['Commodity'],
            delivery_month=row['Delivery Month'],
            price=float(row['Price']),
            counterparty=row.get('Counterparty')
        )
        trades.append(trade)
    return trades

def calculate_net_position(trades: List[Trade]) -> List[Position]:
    if not trades:
        return []

    # Convert to DataFrame for easier aggregation
    data = [t.dict() for t in trades]
    df = pd.DataFrame(data)

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
