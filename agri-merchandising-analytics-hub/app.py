import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics_engine import MerchandisingAnalyst

# 1. Setup
st.set_page_config(
    page_title="Agri-Merchandising Analytics Hub | Cargill Candidate Portfolio",
    layout="wide"
)

st.title("Agri-Merchandising Analytics Hub | Cargill Candidate Portfolio")

# Initialize the analyst engine
@st.cache_resource
def get_analyst():
    return MerchandisingAnalyst()

analyst = get_analyst()

# 2. Sidebar
st.sidebar.header("Commodity Selection")
commodity_choice = st.sidebar.radio("Select Commodity", options=["Corn", "Soybeans"])

# Map to ticker
ticker_map = {
    "Corn": "ZC=F",
    "Soybeans": "ZS=F"
}
ticker = ticker_map[commodity_choice]

st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.info(
    "This tool analyzes Physical Supply/Demand flows to identify market tightness. "
    "Designed to demonstrate robust data pipelines and merchandising analytics."
)

# Fetch Data
balance_sheet = analyst.get_market_tightness(commodity_choice)
prices_df = analyst.get_price_volatility(ticker)
basis_df = analyst.get_simulated_basis(ticker)

if balance_sheet.empty or prices_df.empty:
    st.error("Data could not be loaded. Please ensure data_pipeline.py has been run.")
    st.stop()

# 3. Top Metrics
st.header(f"{commodity_choice} Market Overview (Latest)")

# Latest fundamentals
latest_bs = balance_sheet.iloc[-1]
prev_bs = balance_sheet.iloc[-2] if len(balance_sheet) > 1 else None

latest_ending_stocks = latest_bs['Ending_Stocks']
yoy_ending_stocks = latest_ending_stocks - prev_bs['Ending_Stocks'] if prev_bs is not None else 0

latest_stu = latest_bs['Stocks_to_Use_Ratio']
yoy_stu = latest_stu - prev_bs['Stocks_to_Use_Ratio'] if prev_bs is not None else 0

# Latest price & basis
latest_basis_row = basis_df.iloc[-1]
latest_basis_price = latest_basis_row['Simulated_Cash_Price']
latest_futures_price = latest_basis_row[ticker]
latest_fixed_basis = latest_basis_row['Basis']

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Ending Stocks (2025) [mln bu]",
        value=f"{latest_ending_stocks:,.0f}",
        delta=f"{yoy_ending_stocks:,.0f} YoY",
        delta_color="inverse" # Lower stocks usually mean tighter market, but just visually
    )

with col2:
    st.metric(
        label="Stocks-to-Use Ratio",
        value=f"{latest_stu:.2f}%",
        delta=f"{yoy_stu:.2f}% YoY",
        delta_color="inverse"
    )
    if latest_stu < 10.0:
        st.markdown('<p style="color:red;font-size:14px;margin-top:-15px;"><strong>Critically tight (&lt;10%)</strong></p>', unsafe_allow_html=True)

with col3:
    st.metric(
        label="Simulated Cash Price ($/bu)",
        value=f"${latest_basis_price:,.2f}",
        delta=f"Basis: {latest_fixed_basis:.2f}",
        delta_color="off"
    )

st.markdown("---")

# 4. Visuals (Plotly)
st.header("Visual Analytics")
st.subheader("1. Supply/Demand Balance")

# Grouped bar chart: Production, Total Use, Ending Stocks
chart_df = balance_sheet.copy()
chart_df['Total_Use'] = chart_df['Domestic_Use'] + chart_df['Exports']

fig_sd = go.Figure()
fig_sd.add_trace(go.Bar(x=chart_df['Year'], y=chart_df['Production'], name='Production'))
fig_sd.add_trace(go.Bar(x=chart_df['Year'], y=chart_df['Total_Use'], name='Total Use'))
fig_sd.add_trace(go.Bar(x=chart_df['Year'], y=chart_df['Ending_Stocks'], name='Ending Stocks'))

fig_sd.update_layout(
    barmode='group',
    xaxis_title='Year',
    yaxis_title='Millions of Bushels',
    title='Production vs Total Use vs Ending Stocks'
)
st.plotly_chart(fig_sd, use_container_width=True)


col1, col2 = st.columns(2)

with col1:
    st.subheader("2. Market Tightness Trend")
    fig_stu = go.Figure()
    fig_stu.add_trace(go.Scatter(
        x=chart_df['Year'], 
        y=chart_df['Stocks_to_Use_Ratio'],
        mode='lines+markers',
        name='Stocks-to-Use %',
        line=dict(width=3)
    ))
    
    # Add dashed red line at 10%
    fig_stu.add_hline(
        y=10.0, 
        line_dash="dash", 
        line_color="red", 
        annotation_text="Critical Bottleneck (10%)"
    )
    
    fig_stu.update_layout(
        xaxis_title='Year',
        yaxis_title='Stocks-to-Use Ratio (%)',
        title='S&D Tightness Over Time'
    )
    st.plotly_chart(fig_stu, use_container_width=True)

with col2:
    st.subheader("3. Price Momentum")
    
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(
        x=prices_df.index, 
        y=prices_df[ticker],
        mode='lines',
        name=f'{ticker} Futures Price'
    ))
    
    fig_price.update_layout(
        xaxis_title='Date',
        yaxis_title='Price',
        title=f'{commodity_choice} Futures Price Trend ({ticker})'
    )
    st.plotly_chart(fig_price, use_container_width=True)


# 5. Actionable Insights
st.header("Actionable Insights")
if latest_stu < 10.0:
    st.warning("S&D TIGHTNESS DETECTED: Recommend prioritizing supply security and monitoring export pace.")
else:
    st.info("ADEQUATE SUPPLY: Market appears well-supplied. Focus on basis optimization and managing storage carrying costs.")

# 6. Cleanliness - Raw Data
st.markdown("---")
st.subheader("Raw Balance Sheet Data")
st.dataframe(balance_sheet, use_container_width=True)
