import xlwings as xw
import pandas as pd
from app.core.curve_engine import ForwardCurve
from app.core.pnl_engine import decompose_pnl
from app.core.arb_engine import OilArbCalculator

# ... (imports)

def run_arb_calc():
    """
    Runs Oil Arbitrage calculation (WTI-Brent) and updates matrix.
    """
    wb = xw.Book.caller()
    sheet = wb.sheets['Global_Arb']
    
    # Initialize Calculator (Aframax 700kbbl)
    calc = OilArbCalculator(volume_bbl=700000)
    
    # Define Routes (Mock)
    routes = [
        {"name": "Aframax USGC-Rotterdam", "ws": 110, "flat": 25.50, "volume": 700000},
        {"name": "Suezmax USGC-Rotterdam", "ws": 85, "flat": 25.50, "volume": 1000000},
        {"name": "VLCC USGC-Rotterdam", "ws": 60, "flat": 25.50, "volume": 2000000}
    ]
    
    # Run Optimization
    results = calc.optimize_logistics(routes)
    
    # Write to Excel
    sheet.range('A1').value = "Route"
    sheet.range('B1').value = "Net Margin ($/bbl)"
    sheet.range('C1').value = "Total Profit ($)"
    
    row = 2
    for scenario in results['all_scenarios']:
        sheet.range(f'A{row}').value = scenario['route_name']
        sheet.range(f'B{row}').value = scenario['net_margin_per_bbl']
        sheet.range(f'C{row}').value = scenario['total_profit']
        
        # Highlight best route
        if scenario['route_name'] == results['best_route']:
            sheet.range(f'A{row}:C{row}').color = (0, 255, 0) # Green
        
        row += 1

if __name__ == "__main__":
    # This allows running the script to test without Excel
    xw.Book("etos_dashboard.xlsx").set_mock_caller()
    run_validation()
