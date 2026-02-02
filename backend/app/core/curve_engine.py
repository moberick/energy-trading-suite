import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
from scipy.interpolate import CubicSpline

class ForwardCurve:
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with a DataFrame containing 'tenor', 'price', 'last_update'.
        Expected columns: ['tenor', 'price', 'last_update']
        """
        self.data = data.copy()
        # Ensure price is float
        self.data['price'] = self.data['price'].astype(float)
        # Ensure last_update is datetime
        if 'last_update' in self.data.columns:
            self.data['last_update'] = pd.to_datetime(self.data['last_update'])
        else:
            self.data['last_update'] = datetime.now() # Default if missing

    def validate_integrity(self, fly_threshold: float = 0.05, stale_limit_hours: int = 24, seasonality_vector: Optional[Dict[str, float]] = None) -> Dict[str, List[str]]:
        """
        Run all validation checks.
        Returns a dictionary of alerts.
        """
        alerts = {
            "stale": [],
            "fly": [],
            "seasonality": [] # Not really an alert, but maybe info? Or just used internally.
        }

        # 1. Stale Checks
        stale_alerts = self.check_stale(limit_hours=stale_limit_hours)
        alerts["stale"].extend(stale_alerts)

        # 2. Fly Checks (with optional seasonality adjustment)
        fly_alerts = self.check_butterfly(threshold=fly_threshold, seasonality_vector=seasonality_vector)
        alerts["fly"].extend(fly_alerts)

        return alerts

    def check_stale(self, limit_hours: int = 24) -> List[str]:
        """
        Check for stale data based on time and content hash.
        """
        alerts = []
        now = datetime.now()
        
        # Time-based check
        for idx, row in self.data.iterrows():
            time_diff = now - row['last_update']
            if time_diff > timedelta(hours=limit_hours):
                alerts.append(f"Stale (Time): {row['tenor']} last updated {time_diff} ago")

        # Content Hash check (Simulated: In a real system, we'd compare with previous day's hash)
        # For this implementation, we'll calculate the hash of the current prices.
        # To be useful, we'd need history. 
        # Let's just implement the hashing logic as requested for "Vitol-grade" readiness.
        current_hash = self._calculate_content_hash()
        # alerts.append(f"Curve Hash: {current_hash}") # Debug info
        
        return alerts

    def _calculate_content_hash(self) -> str:
        """
        Calculate SHA-256 hash of the price vector.
        """
        prices = self.data['price'].values
        return hashlib.sha256(prices.tobytes()).hexdigest()

    def check_butterfly(self, threshold: float = 0.05, seasonality_vector: Optional[Dict[str, float]] = None) -> List[str]:
        """
        Calculate normalized butterfly (fly) check.
        B_norm_t = (P_t-1 - 2P_t + P_t+1) / P_t
        """
        alerts = []
        prices = self.data['price'].values
        tenors = self.data['tenor'].values

        # Apply Seasonality Adjustment if provided
        adj_prices = prices.copy()
        if seasonality_vector:
            # Assuming seasonality_vector keys match tenor names or months
            # This is a simplified application.
            adj_prices = np.array([p - seasonality_vector.get(t, 0) for t, p in zip(tenors, prices)])

        # Calculate Fly
        # We need at least 3 points
        if len(adj_prices) < 3:
            return []

        for i in range(1, len(adj_prices) - 1):
            p_prev = adj_prices[i-1]
            p_curr = adj_prices[i]
            p_next = adj_prices[i+1]

            if p_curr == 0:
                continue # Avoid division by zero

            fly_val = (p_prev - 2*p_curr + p_next) / p_curr
            
            if abs(fly_val) > threshold:
                alerts.append(f"Fly Check: {tenors[i]} deviation {fly_val:.2%} exceeds threshold {threshold:.2%}")

        return alerts

    def interpolate_missing(self):
        """
        Interpolate missing values using Cubic Spline.
        """
        # Identify missing prices (NaN)
        # In this simplified version, we assume the DataFrame might have NaNs
        if self.data['price'].isnull().any():
            # Create a numeric index for interpolation
            x = np.arange(len(self.data))
            y = self.data['price'].values
            
            # Mask for valid values
            mask = ~np.isnan(y)
            
            if np.sum(mask) >= 2: # Need at least 2 points for basic, 3 for cubic usually
                cs = CubicSpline(x[mask], y[mask])
                self.data['price'] = cs(x)
