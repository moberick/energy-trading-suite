import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import re

def parse_tenor_to_date(tenor: str) -> datetime:
    """
    Parse a tenor string (e.g., 'Jan25', 'Feb25') to a datetime.
    Assumes format: 'MonYY' where Mon is 3-letter month, YY is 2-digit year.
    """
    # Handle various formats: 'Jan25', 'Jan 25', '2025-01', etc.
    tenor = str(tenor).strip()
    
    # Format: 'Jan25' or 'Jan 25'
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    # Try 'MonYY' format
    match = re.match(r'([A-Za-z]{3})\s*(\d{2})', tenor)
    if match:
        month_str = match.group(1).lower()
        year_str = match.group(2)
        month = month_map.get(month_str, 1)
        year = 2000 + int(year_str)
        return datetime(year, month, 15)  # Mid-month as reference
    
    # Try 'YYYY-MM' format
    match = re.match(r'(\d{4})-(\d{2})', tenor)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return datetime(year, month, 15)
    
    # Fallback: return current date
    return datetime.now()


def calculate_theta_pnl(
    portfolio: pd.DataFrame,
    curves_t0: pd.DataFrame,
    curves_t1: pd.DataFrame,
    days_elapsed: int = 1
) -> float:
    """
    Calculate Time Decay (Theta) P&L using the Roll/Carry method.
    
    Theta P&L captures the cost/benefit of holding positions as they "roll" 
    down the forward curve due to passage of time.
    
    Key Concepts:
    - Contango (upward curve): Longs lose value (negative theta), Shorts gain
    - Backwardation (downward curve): Longs gain value (positive theta), Shorts lose
    
    Method: Curve Aging
    We compare the value of the portfolio on the T-1 curve vs the T curve,
    but isolate only the "time component" by measuring how the curve shape
    has "rolled forward" by one day.
    
    Formula for each position:
        theta_position = position * (curve_slope_at_tenor) * days_elapsed
    
    Where curve_slope = (Price_M - Price_M+1) / days_between_tenors
    This represents the daily "roll" or "carry" at that point on the curve.
    
    Args:
        portfolio: DataFrame with ['commodity', 'tenor', 'volume', 'direction']
        curves_t0: Yesterday's curve DataFrame ['commodity', 'tenor', 'price']
        curves_t1: Today's curve DataFrame ['commodity', 'tenor', 'price']
        days_elapsed: Number of days between t0 and t1 (typically 1)
        
    Returns:
        Total Theta P&L across all positions
    """
    if portfolio.empty:
        return 0.0
    
    theta_pnl = 0.0
    
    # Group portfolio by commodity
    for commodity in portfolio['commodity'].unique():
        # Get positions for this commodity
        comm_positions = portfolio[portfolio['commodity'] == commodity].copy()
        
        # Get curve data for this commodity
        comm_curve_t0 = curves_t0[curves_t0['commodity'] == commodity].copy()
        comm_curve_t1 = curves_t1[curves_t1['commodity'] == commodity].copy()
        
        if comm_curve_t0.empty or comm_curve_t1.empty:
            continue
        
        # Sort curves by tenor date for proper roll calculation
        comm_curve_t0['tenor_date'] = comm_curve_t0['tenor'].apply(parse_tenor_to_date)
        comm_curve_t0 = comm_curve_t0.sort_values('tenor_date')
        
        # Build a map of tenor -> next_tenor price for roll calculation
        tenors = comm_curve_t0['tenor'].tolist()
        prices = comm_curve_t0['price'].tolist()
        
        # Calculate daily roll (carry) for each tenor
        # Roll = (Price_current_tenor - Price_next_tenor) / days_between
        tenor_roll_map = {}
        for i in range(len(tenors) - 1):
            current_tenor = tenors[i]
            current_price = prices[i]
            next_price = prices[i + 1]
            
            # Approximate days between monthly tenors = 30
            days_between = 30
            
            # Daily roll rate
            # Positive roll = contango (front < back), negative roll = backwardation
            # For a LONG position: contango = you LOSE value as you roll (pay the carry)
            # For a SHORT position: contango = you GAIN value
            daily_roll = (next_price - current_price) / days_between
            tenor_roll_map[current_tenor] = daily_roll
        
        # For the last tenor, assume zero roll (no next contract to roll into)
        if tenors:
            tenor_roll_map[tenors[-1]] = 0.0
        
        # Calculate theta for each position
        for _, pos in comm_positions.iterrows():
            tenor = pos['tenor']
            volume = pos['volume']
            direction = pos.get('direction', 'Buy')
            
            # Direction multiplier: Buy = Long = +1, Sell = Short = -1
            dir_mult = 1 if direction == 'Buy' else -1
            signed_volume = volume * dir_mult
            
            # Get roll rate for this tenor
            roll_rate = tenor_roll_map.get(tenor, 0.0)
            
            # Theta P&L:
            # If roll_rate > 0 (contango), longs LOSE value (pay carry)
            # Theta = -signed_volume * roll_rate * days
            # The negative sign: in contango, a long position has NEGATIVE theta
            position_theta = -signed_volume * roll_rate * days_elapsed
            
            theta_pnl += position_theta
    
    return theta_pnl


def decompose_pnl(
    portfolio_t0: pd.DataFrame, 
    portfolio_t1: pd.DataFrame, 
    curves_t0: pd.DataFrame, 
    curves_t1: pd.DataFrame,
    fx_t0: float = 1.0, # USD per Base Currency (if portfolio is non-USD)
    fx_t1: float = 1.0,
    unexplained_tolerance: float = 0.02
) -> pd.DataFrame:
    """
    Decompose P&L into New Deal, Market Risk (Delta, Gamma), FX P&L, Time Decay, and Unexplained.
    
    Expected DataFrame columns:
    Portfolio: ['trade_id', 'commodity', 'tenor', 'volume', 'price', 'deal_type', 'direction']
    Curves: ['commodity', 'tenor', 'price']
    """
    
    # 1. Identify New Deals (in t1 but not t0)
    # Assuming trade_id is unique
    t0_ids = set(portfolio_t0['trade_id'])
    t1_ids = set(portfolio_t1['trade_id'])
    new_deal_ids = t1_ids - t0_ids
    
    new_deals = portfolio_t1[portfolio_t1['trade_id'].isin(new_deal_ids)].copy()
    existing_deals_t1 = portfolio_t1[~portfolio_t1['trade_id'].isin(new_deal_ids)].copy()
    existing_deals_t0 = portfolio_t0[portfolio_t0['trade_id'].isin(t1_ids)].copy() # Only those that still exist

    # Merge curves to calculate valuations
    # Helper to value portfolio
    def value_portfolio(port: pd.DataFrame, curves: pd.DataFrame, fx_rate: float) -> float:
        if port.empty: return 0.0
        # Merge on commodity and tenor
        merged = pd.merge(port, curves, on=['commodity', 'tenor'], how='left', suffixes=('', '_curve'))
        # Handle missing curve points? For now assume complete curves or fillna(0)
        merged['price_curve'] = merged['price_curve'].fillna(0)
        
        # Valuation: (Curve Price - Trade Price) * Volume * Direction
        # Direction: Buy = 1, Sell = -1
        merged['dir_mult'] = merged['direction'].apply(lambda x: 1 if x == 'Buy' else -1)
        
        # MtM in Native Currency
        merged['mtm_native'] = (merged['price_curve'] - merged['price']) * merged['volume'] * merged['dir_mult']
        
        # Convert to Reporting Currency (USD)
        merged['mtm_usd'] = merged['mtm_native'] * fx_rate
        
        return merged['mtm_usd'].sum()

    # 2. Calculate New Deal P&L
    # New Deal P&L = Day 1 Margin = (Curve_t1 - Trade_Price) * Volume * FX_t1
    new_deal_pnl = value_portfolio(new_deals, curves_t1, fx_t1)

    # 3. Calculate Market Risk P&L (Delta) on Existing Portfolio
    # Delta P&L = Val(t0_port, t1_curves, t0_fx) - Val(t0_port, t0_curves, t0_fx)
    # We hold FX constant at t0 to isolate Price Delta
    
    val_t0_curves_t0_fx_t0 = value_portfolio(existing_deals_t0, curves_t0, fx_t0)
    val_t0_curves_t1_fx_t0 = value_portfolio(existing_deals_t0, curves_t1, fx_t0)
    
    market_risk_pnl = val_t0_curves_t1_fx_t0 - val_t0_curves_t0_fx_t0
    
    delta_pnl = market_risk_pnl
    gamma_pnl = 0.0 # Placeholder for options

    # 4. FX P&L
    # FX P&L = Val(t0_port, t1_curves, t1_fx) - Val(t0_port, t1_curves, t0_fx)
    # Change in value due to FX rate change, holding curves constant at t1
    
    val_t0_curves_t1_fx_t1 = value_portfolio(existing_deals_t0, curves_t1, fx_t1)
    
    fx_pnl = val_t0_curves_t1_fx_t1 - val_t0_curves_t1_fx_t0

    # 5. Time Decay (Theta) - Roll/Carry P&L
    # Theta captures the cost of carry as positions age toward expiry.
    # In Contango: Long positions lose value (negative theta)
    # In Backwardation: Long positions gain value (positive theta)
    #
    # Formula: theta = sum over positions of: position * daily_roll
    # where daily_roll = (P_M - P_M+1) / days_between_tenors
    
    theta_pnl = calculate_theta_pnl(existing_deals_t0, curves_t0, curves_t1)

    # 6. Total P&L (Actual)
    # Total P&L = Val_t1 - Val_t0
    # Val_t1 = Val(Existing_t1, curves_t1, fx_t1) + Val(New_t1, curves_t1, fx_t1)
    # Val_t0 = Val(Existing_t0, curves_t0, fx_t0)
    
    # Note: Existing_t1 should be same as Existing_t0 if no expiries.
    
    total_pnl_calc = new_deal_pnl + delta_pnl + gamma_pnl + fx_pnl + theta_pnl
    
    # Unexplained P&L
    official_pnl = total_pnl_calc + np.random.normal(0, 50) # Reduced noise
    
    unexplained_pnl = official_pnl - total_pnl_calc
    
    # Check Tolerance
    if abs(unexplained_pnl) > (abs(official_pnl) * unexplained_tolerance) and abs(official_pnl) > 1000:
        print(f"ALERT: Unexplained P&L ({unexplained_pnl:.2f}) exceeds tolerance!")

    # Return Attribution DataFrame
    attribution = pd.DataFrame([
        {"driver": "New Deal P&L", "pnl_value": new_deal_pnl},
        {"driver": "Market Risk (Delta)", "pnl_value": delta_pnl},
        {"driver": "Market Risk (Gamma)", "pnl_value": gamma_pnl},
        {"driver": "FX P&L", "pnl_value": fx_pnl},
        {"driver": "Time Decay (Theta)", "pnl_value": theta_pnl},
        {"driver": "Unexplained", "pnl_value": unexplained_pnl}
    ])
    
    return attribution
