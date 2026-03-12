import os
import pandas as pd
import numpy as np

class MerchandisingAnalyst:
    def __init__(self, data_dir='data'):
        """
        Initializes the Merchandising Analyst by loading market data and fundamental supply & demand data.
        """
        self.data_dir = data_dir
        
        # Use relative paths from the script execution context
        base_dir = os.path.dirname(os.path.abspath(__file__))
        market_path = os.path.join(base_dir, self.data_dir, 'market_prices.csv')
        supply_demand_path = os.path.join(base_dir, self.data_dir, 'supply_demand.csv')
        
        try:
            # Parse dates for market prices and set the date as index
            self.market_df = pd.read_csv(market_path, parse_dates=['Date'])
            self.market_df.set_index('Date', inplace=True)
            self.fundamentals_df = pd.read_csv(supply_demand_path)
            # print(f"Successfully loaded data. Market data: {len(self.market_df)} rows, Fundamentals: {len(self.fundamentals_df)} rows.")
        except FileNotFoundError as e:
            print(f"Error loading data: {e}. Please ensure data_pipeline.py has been run successfully.")
            self.market_df = pd.DataFrame()
            self.fundamentals_df = pd.DataFrame()
            
    def get_balance_sheet(self, commodity: str) -> pd.DataFrame:
        """
        Filters fundamentals data by commodity and calculates Ending Stocks and Stocks-to-Use Ratio.
        """
        if self.fundamentals_df.empty:
            return pd.DataFrame()
            
        # Filter by commodity (case insensitive)
        df = self.fundamentals_df[self.fundamentals_df['Commodity'].str.lower() == commodity.lower()].copy()
        
        if df.empty:
            print(f"Warning: No data found for commodity '{commodity}'")
            return pd.DataFrame()
            
        # Calculate Ending Stocks
        # Ending Stocks = (Beginning_Stocks + Production + Imports) - (Domestic_Use + Exports)
        df['Ending_Stocks'] = (df['Beginning_Stocks'] + df['Production'] + df['Imports']) - (df['Domestic_Use'] + df['Exports'])
        
        # Calculate Stocks-to-Use Ratio (%)
        total_use = df['Domestic_Use'] + df['Exports']
        # Handle division by zero
        df['Stocks_to_Use_Ratio'] = np.where(total_use > 0, (df['Ending_Stocks'] / total_use) * 100, 0)
        
        return df

    def get_market_tightness(self, commodity: str) -> pd.DataFrame:
        """
        Identifies 'Supply Bottlenecks' where the Stocks-to-Use Ratio falls below 10%.
        """
        df = self.get_balance_sheet(commodity)
        if df.empty:
            return pd.DataFrame()
            
        # Flag 'Supply Bottleneck' if ratio is below 10%
        df['Market_Tightness_Flag'] = np.where(df['Stocks_to_Use_Ratio'] < 10.0, 'Supply Bottleneck', 'Adequate Supply')
        
        return df
        
    def get_price_volatility(self, commodity_ticker: str) -> pd.DataFrame:
        """
        Calculates the 30-day rolling volatility for the given futures ticker to demonstrate 'Risk Appetite'.
        """
        if self.market_df.empty or commodity_ticker not in self.market_df.columns:
            print(f"Warning: Ticker '{commodity_ticker}' not found in market data.")
            return pd.DataFrame()
            
        # Get price series for the commodity and drop NAs
        prices = self.market_df[[commodity_ticker]].dropna().copy()
        
        # Calculate daily logarithmic returns
        prices['Daily_Return'] = np.log(prices[commodity_ticker] / prices[commodity_ticker].shift(1))
        
        # Calculate 30-day rolling standard deviation of daily returns
        prices['30D_Rolling_Volatility'] = prices['Daily_Return'].rolling(window=30).std()
        
        # Return cleaned dataframe
        return prices
        
    def get_simulated_basis(self, commodity_ticker: str, fixed_basis: float = 0.20) -> pd.DataFrame:
        """
        Simulates a 'Basis' by subtracting a fixed amount (default $0.20/bu) from the futures price.
        """
        if self.market_df.empty or commodity_ticker not in self.market_df.columns:
            print(f"Warning: Ticker '{commodity_ticker}' not found in market data.")
            return pd.DataFrame()
            
        prices = self.market_df[[commodity_ticker]].dropna().copy()
        prices['Simulated_Cash_Price'] = prices[commodity_ticker] - fixed_basis
        prices['Basis'] = -fixed_basis  # Basis = Cash - Futures
        
        return prices


if __name__ == "__main__":
    # Quick sanity check
    analyst = MerchandisingAnalyst()
    print("--- Balance Sheet & Market Tightness for Corn ---")
    corn_bs = analyst.get_market_tightness("Corn")
    print(corn_bs)
    
    print("\n--- Price Volatility for Corn (ZC=F) (Last 5 Rows) ---")
    corn_vol = analyst.get_price_volatility("ZC=F")
    print(corn_vol.tail())
    
    print("\n--- Simulated Basis for Soybeans (ZS=F) (Last 5 Rows) ---")
    soy_basis = analyst.get_simulated_basis("ZS=F")
    print(soy_basis.tail())
