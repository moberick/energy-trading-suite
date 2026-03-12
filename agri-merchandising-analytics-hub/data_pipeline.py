import os
import pandas as pd
import yfinance as yf

def main():
    # 1. Directory Check
    # Use absolute path based on the script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
    else:
        print(f"Directory already exists: {data_dir}")

    # 2. Market Data Fetching
    print("Fetching market data for Corn (ZC=F) and Soybeans (ZS=F)...")
    tickers = ["ZC=F", "ZS=F"]
    
    # Fetch last 12 months (1y) of daily data
    # yf.download returns a multi-index column dataframe when querying multiple tickers
    data = yf.download(tickers, period="1y", interval="1d")
    
    # Try to extract 'Adj Close', fallback to 'Close'
    if 'Adj Close' in data.columns.get_level_values(0):
        prices = data['Adj Close']
    elif 'Close' in data.columns.get_level_values(0):
        prices = data['Close']
    else:
        # Fallback if the structure is unexpected
        prices = data

    market_file = os.path.join(data_dir, 'market_prices.csv')
    prices.to_csv(market_file)
    print(f"SUCCESS: Saved market data ({len(prices)} rows) to {market_file}")

    # 3. Fundamentals Generation
    # Creating a synthetic WASDE-style dataset for 2021-2025
    
    # Corn (in millions of bushels, typical USDA scale)
    # tightening logic for 24/25: lower production, higher exports -> lower ending stocks
    corn_data = [
        [2021, 1236, 15074, 24, 12484, 2471], # End = 1379
        [2022, 1379, 13730, 39, 12101, 1661], # End = 1386
        [2023, 1386, 15342, 25, 12540, 2122], # End = 2091
        [2024, 2091, 14890, 25, 12665, 2350], # End = 1991 (Tightening begins)
        [2025, 1991, 14200, 25, 12700, 2450], # End = 1066 (Sharp tightening)
    ]
    corn_df = pd.DataFrame(
        corn_data, 
        columns=['Year', 'Beginning_Stocks', 'Production', 'Imports', 'Domestic_Use', 'Exports']
    )
    corn_df.insert(1, 'Commodity', 'Corn')

    # Soybeans (in millions of bushels)
    # tightening logic for 24/25
    soy_data = [
        [2021, 256, 4465, 16, 2205, 2158], # End = 374
        [2022, 374, 4270, 25, 2314, 1992], # End = 363
        [2023, 363, 4165, 15, 2296, 1700], # End = 547
        [2024, 547, 4250, 15, 2420, 1850], # End = 542 (Tightening)
        [2025, 542, 3900, 15, 2450, 1950], # End =   57 (Sharp tightening)
    ]
    soy_df = pd.DataFrame(
        soy_data, 
        columns=['Year', 'Beginning_Stocks', 'Production', 'Imports', 'Domestic_Use', 'Exports']
    )
    soy_df.insert(1, 'Commodity', 'Soybeans')

    # Combine both dataframes
    fundamentals_df = pd.concat([corn_df, soy_df], ignore_index=True)
    
    fund_file = os.path.join(data_dir, 'supply_demand.csv')
    fundamentals_df.to_csv(fund_file, index=False)
    print(f"SUCCESS: Saved fundamentals data ({len(fundamentals_df)} rows) to {fund_file}")

if __name__ == "__main__":
    main()
