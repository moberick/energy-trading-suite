# Agri-Merchandising Analytics Hub

## Executive Summary

The **Agri-Merchandising Analytics Hub** is a dynamic portfolio project designed to demonstrate robust data pipeline engineering, sophisticated market analysis, and interactive dashboard creation. By ingesting real-world market prices and synthesizing fundamental supply & demand metrics for key agricultural commodities (Corn and Soybeans), this tool provides actionable merchandising insights.

### Key Features
1. **Data Pipeline Automation (`data_pipeline.py`)**: Seamlessly structured to fetch historical market data via `yfinance` and generate synthetically accurate WASDE-style supply/demand fundamentals, simulating a real-world data engineering environment.
2. **Merchandising Analytics Engine (`analytics_engine.py`)**: Features a robust object-oriented class (`MerchandisingAnalyst`) that computes critical merchandising metrics, including:
   - **Balance Sheet Construction**: Accurately calculates Ending Stocks and Stocks-to-Use Ratios.
   - **Market Tightness Logic**: Automatically flags commodities with critical supply bottlenecks (sub-10% Stocks-to-Use ratio).
   - **Price Volatility Tracking**: Leverages 30-day rolling variance to gauge risk appetite.
   - **Basis Proxies**: Simulates local cash basis trading dynamics to demonstrate real-world physical trading applications.
3. **Interactive Dashboard (`app.py`)**: A Streamlit-powered UI allowing users to toggle between commodities and instantly view performance metrics, Plotly-powered grouped bar charts for S&D balance, price trendlines, and automated actionable strategy suggestions based on the fundamental tightness of the market.

### Setup & Usage
1. Make sure your Python environment has the necessary dependencies installed from `requirements.txt`.
2. Generate the data by running: `python data_pipeline.py`.
3. Launch the Streamlit dashboard by running: `streamlit run app.py`.

This project highlights a solid understanding of both full-stack Python development and the economic fundamentals of global agriculture merchandising.
