import pandas as pd
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.arb_engine import OilArbCalculator
from app.core.pnl_engine import decompose_pnl
from app.services.data_manager import DataManager

def test_oil_arb():
    print("\n--- Testing Oil Arbitrage ---")
    calc = OilArbCalculator(volume_bbl=700000)
    res = calc.calculate_economics(
        wti_price=70.0,
        brent_price=75.0,
        freight_rate_flat=20.0,
        ws_points=100.0
    )
    print("Result:", res)
    
    assert res['gross_spread'] == 5.0
    assert res['freight_per_bbl'] > 0
    assert 'net_margin_per_bbl' in res
    print("✅ Oil Arb Test Passed")

def test_fx_pnl():
    print("\n--- Testing FX P&L ---")
    # Setup Dummy Data
    portfolio_t0 = pd.DataFrame([
        {'trade_id': 1, 'commodity': 'Brent', 'tenor': 'Jan25', 'volume': 1000, 'price': 70, 'direction': 'Buy'}
    ])
    portfolio_t1 = portfolio_t0.copy()
    
    curves_t0 = pd.DataFrame([{'commodity': 'Brent', 'tenor': 'Jan25', 'price': 72}])
    curves_t1 = pd.DataFrame([{'commodity': 'Brent', 'tenor': 'Jan25', 'price': 72}]) # No price change
    
    # FX Change: 1.0 -> 1.10 (USD getting weaker or Base getting stronger? 
    # Logic was: Mtm_USD = Mtm_Native * FX. 
    # If Native is EUR, FX is USD/EUR. 
    # Let's say Mtm_Native is 2000 (72-70 * 1000).
    # FX t0 = 1.0 -> USD 2000.
    # FX t1 = 1.1 -> USD 2200.
    # FX P&L should be +200.
    
    attribution = decompose_pnl(
        portfolio_t0, portfolio_t1, curves_t0, curves_t1,
        fx_t0=1.0, fx_t1=1.1
    )
    
    print(attribution)
    
    fx_pnl = attribution[attribution['driver'] == 'FX P&L']['pnl_value'].values[0]
    print(f"FX P&L: {fx_pnl}")
    
    # Expected: (2000 * 1.1) - (2000 * 1.0) = 2200 - 2000 = 200
    assert abs(fx_pnl - 200.0) < 0.01
    print("✅ FX P&L Test Passed")

def test_position_aggregation():
    print("\n--- Testing Position Aggregation ---")
    dm = DataManager()
    # Mock data
    dm.trades_df = pd.DataFrame([
        {'trade_id': 1, 'commodity': 'WTI', 'tenor': 'Jan25', 'volume': 1000, 'direction': 'Buy'},
        {'trade_id': 2, 'commodity': 'WTI', 'tenor': 'Jan25', 'volume': 1000, 'direction': 'Sell'}, # Net 0
        {'trade_id': 3, 'commodity': 'Brent', 'tenor': 'Feb25', 'volume': 500, 'direction': 'Buy'}  # Net 500 Long
    ])
    
    exposure = dm.aggregate_positions()
    print(exposure)
    
    wti_exp = exposure[(exposure['commodity'] == 'WTI') & (exposure['tenor'] == 'Jan25')]['net_volume'].values[0]
    brent_exp = exposure[(exposure['commodity'] == 'Brent') & (exposure['tenor'] == 'Feb25')]['net_volume'].values[0]
    
    assert wti_exp == 0
    assert brent_exp == 500
    print("✅ Position Aggregation Test Passed")


def test_theta_pnl():
    """
    Test Time Decay (Theta) P&L in Contango and Backwardation scenarios.
    
    Interview Defense Points:
    - Contango: Long positions have NEGATIVE theta (you pay the carry)
    - Backwardation: Long positions have POSITIVE theta (you earn the carry)
    """
    from app.core.pnl_engine import calculate_theta_pnl
    
    print("\n--- Testing Theta P&L (Time Decay) ---")
    
    # Scenario 1: CONTANGO (upward sloping curve)
    # Prices: Jan25=$70, Feb25=$72, Mar25=$74
    # A LONG position should have NEGATIVE theta (you lose value rolling forward)
    print("\n  Scenario 1: Contango - Long Position")
    
    portfolio_contango = pd.DataFrame([
        {'commodity': 'Brent', 'tenor': 'Jan25', 'volume': 1000, 'direction': 'Buy'}
    ])
    
    curves_contango = pd.DataFrame([
        {'commodity': 'Brent', 'tenor': 'Jan25', 'price': 70.0},
        {'commodity': 'Brent', 'tenor': 'Feb25', 'price': 72.0},
        {'commodity': 'Brent', 'tenor': 'Mar25', 'price': 74.0}
    ])
    
    theta_contango = calculate_theta_pnl(portfolio_contango, curves_contango, curves_contango)
    print(f"  Contango Theta (Long 1000 bbl): ${theta_contango:.2f}")
    
    # In contango, long positions should have NEGATIVE theta
    assert theta_contango < 0, f"Expected negative theta in contango for longs, got {theta_contango}"
    print("  ✓ Contango: Long position correctly shows NEGATIVE theta")
    
    # Scenario 2: BACKWARDATION (downward sloping curve)
    # Prices: Jan25=$74, Feb25=$72, Mar25=$70
    # A LONG position should have POSITIVE theta (you gain value rolling forward)
    print("\n  Scenario 2: Backwardation - Long Position")
    
    curves_backwardation = pd.DataFrame([
        {'commodity': 'Brent', 'tenor': 'Jan25', 'price': 74.0},
        {'commodity': 'Brent', 'tenor': 'Feb25', 'price': 72.0},
        {'commodity': 'Brent', 'tenor': 'Mar25', 'price': 70.0}
    ])
    
    theta_backwardation = calculate_theta_pnl(portfolio_contango, curves_backwardation, curves_backwardation)
    print(f"  Backwardation Theta (Long 1000 bbl): ${theta_backwardation:.2f}")
    
    # In backwardation, long positions should have POSITIVE theta
    assert theta_backwardation > 0, f"Expected positive theta in backwardation for longs, got {theta_backwardation}"
    print("  ✓ Backwardation: Long position correctly shows POSITIVE theta")
    
    # Scenario 3: SHORT position in Contango (should be positive - you earn the carry)
    print("\n  Scenario 3: Contango - Short Position")
    
    portfolio_short = pd.DataFrame([
        {'commodity': 'Brent', 'tenor': 'Jan25', 'volume': 1000, 'direction': 'Sell'}
    ])
    
    theta_short_contango = calculate_theta_pnl(portfolio_short, curves_contango, curves_contango)
    print(f"  Contango Theta (Short 1000 bbl): ${theta_short_contango:.2f}")
    
    # Short in contango should have POSITIVE theta (you earn the carry)
    assert theta_short_contango > 0, f"Expected positive theta for shorts in contango, got {theta_short_contango}"
    print("  ✓ Contango: Short position correctly shows POSITIVE theta")
    
    # Verify the math: 
    # Roll rate = (72-70)/30 = $0.0667/day per barrel
    # Theta = -1000 * 0.0667 * 1 = -$66.67 (for Long in contango)
    expected_theta = -1000 * ((72-70)/30) * 1
    tolerance = 0.01
    assert abs(theta_contango - expected_theta) < tolerance, f"Math check failed: expected {expected_theta}, got {theta_contango}"
    print(f"  ✓ Math verified: Roll=${((72-70)/30):.4f}/day, Theta=${expected_theta:.2f}")
    
    print("\n✅ Theta P&L Test Passed - All scenarios verified")


if __name__ == "__main__":
    test_oil_arb()
    test_fx_pnl()
    test_position_aggregation()
    test_theta_pnl()
