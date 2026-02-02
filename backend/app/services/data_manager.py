import pandas as pd
import os
from typing import List, Dict, Any
from app.models.trade import Trade, Position
from app.models.curve import CurvePoint
from app.models.pnl import PnLInput, PnLResult # PnLResult might not be the right model for the CSV data, we might need a new one or use a dict for now. 
# Actually the plan said "Add PnLAttribution model". I should do that first. 
# But I can write this file and import it later or just use dicts for now.
# Let's stick to the plan and create the models first/concurrently. 
# I'll use a generic approach for now and refine imports.

class DataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            # __file__ is backend/app/services/data_manager.py
            # dirname -> backend/app/services
            # dirname -> backend/app
            # dirname -> backend
            # dirname -> scratch
            # join(scratch, "data") -> scratch/data
            cls._instance.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
            cls._instance.trades_df = None
            cls._instance.curve_df = None
            cls._instance.pnl_df = None
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        with open("debug.log", "a") as f:
            f.write(f"Loading data from {self.data_dir}\n")
        try:
            self.trades_df = pd.read_csv(os.path.join(self.data_dir, "trades.csv"))
            self.curve_df = pd.read_csv(os.path.join(self.data_dir, "forward_curve.csv"))
            self.pnl_df = pd.read_csv(os.path.join(self.data_dir, "pnl_attribution.csv"))
            with open("debug.log", "a") as f:
                f.write("Data loaded successfully\n")
        except Exception as e:
            with open("debug.log", "a") as f:
                f.write(f"Error loading data: {e}\n")

    def get_trades(self) -> pd.DataFrame:
        return self.trades_df

    def get_curve(self) -> pd.DataFrame:
        return self.curve_df

    def get_pnl_attribution(self) -> pd.DataFrame:
        return self.pnl_df

    def aggregate_positions(self) -> pd.DataFrame:
        """
        Aggregate Physical Inventory and Paper Hedges to generate Net Flat Price Exposure.
        """
        if self.trades_df is None or self.trades_df.empty:
            return pd.DataFrame()

        # Ensure numeric volume
        df = self.trades_df.copy()
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
        
        # Apply Direction (Buy = +, Sell = -)
        df['signed_volume'] = df.apply(
            lambda row: row['volume'] if row['direction'] == 'Buy' else -row['volume'], axis=1
        )
        
        # Group by Commodity and Tenor
        # We want to see Net Exposure per month/product
        exposure = df.groupby(['commodity', 'tenor'])['signed_volume'].sum().reset_index()
        
        exposure.rename(columns={'signed_volume': 'net_volume'}, inplace=True)
        
        # Add status/risk flags
        # e.g. if net_volume is not 0, we have flat price risk
        exposure['risk_status'] = exposure['net_volume'].apply(
            lambda x: 'Long' if x > 0 else ('Short' if x < 0 else 'Flat')
        )
        
        return exposure

data_manager = DataManager()
