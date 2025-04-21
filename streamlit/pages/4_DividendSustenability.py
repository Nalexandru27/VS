# Dividend Sustainability
# 4_DividendSustenability.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os

st.set_page_config(page_title="Dividend Sustainability", layout="centered")

# Import necessary modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.db_instance import get_db
from stock.Stock import Stock  # Assuming this is how you import Stock class

st.title("Dividend Sustainability Analysis")

# Check if ticker is selected in session state
if 'selected_ticker' not in st.session_state or st.session_state.selected_ticker is None:
    st.warning("No company selected. Please return to the home page and select a company.")
    st.stop()

# Get the selected ticker from session state
selected_ticker = st.session_state.selected_ticker.upper()

# Display ticker in sidebar for reference
st.sidebar.info(f"Selected company: {selected_ticker}")

# Get database connection
db_crud = get_db()

# Year range selection
min_year = 2013
max_year = 2023
year_range = st.sidebar.slider(
    "Select time period",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Create the stock object
stock = Stock(selected_ticker)

# Create a function to get dividend data
def get_dividend_data(ticker, start_year, end_year):
    dict = {}
    for year in range(start_year, end_year + 1):
        # Company id
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            st.error(f"Company {ticker} not found in the database")
            return None
        
        # Cash flow financial statement id
        cash_flow_financial_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
        if cash_flow_financial_statement_id is None:
            continue  # Skip this year if statement not found
        
        # Dividends paid
        dividends_paid = db_crud.select_financial_data(cash_flow_financial_statement_id, 'dividendPayout')
        if dividends_paid is None or dividends_paid == 'None':
            continue  # Skip this year if no dividend data
        dividends_paid = int(dividends_paid)
        
        # Dividends paid to preferred stock
        dividends_paid_preferred_stock = db_crud.select_financial_data(cash_flow_financial_statement_id, 'dividendPayoutPreferredStock')
        dividends_paid_preferred_stock = int(dividends_paid_preferred_stock) if dividends_paid_preferred_stock and dividends_paid_preferred_stock != 'None' else 0
        
        # Operating cash flow
        operating_cash_flow = db_crud.select_financial_data(cash_flow_financial_statement_id, 'operatingCashFlow')
        if operating_cash_flow is None or operating_cash_flow == 'None':
            operating_cash_flow = db_crud.select_financial_data(cash_flow_financial_statement_id, 'operatingCashFow')
        
        operating_cash_flow = int(operating_cash_flow) if operating_cash_flow and operating_cash_flow != 'None' else 0

        # Capital expenditures
        capex = db_crud.select_financial_data(cash_flow_financial_statement_id, 'capitalExpenditures')
        capex = int(capex) if capex and capex != 'None' else 0
        
        # Balance sheet financial statement id
        balance_sheet_financial_statement_id = db_crud.select_financial_statement(company_id, 'balance_sheet', year)
        if balance_sheet_financial_statement_id is None:
            continue  # Skip this year if statement not found
        
        # Shares outstanding
        shares_outstanding = db_crud.select_financial_data(balance_sheet_financial_statement_id, 'sharesOutstanding')
        if shares_outstanding is None or shares_outstanding == 'None':
            continue  # Skip this year if no shares data
        shares_outstanding = int(shares_outstanding)
        
        # Income statement financial statement id
        income_statement_financial_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
        if income_statement_financial_statement_id is None:
            continue  # Skip this year if statement not found
        
        # Net income
        net_income = db_crud.select_financial_data(income_statement_financial_statement_id, 'netIncome')
        net_income = int(net_income) if net_income and net_income != 'None' else 0
        
        # EPS per share
        eps_per_share = (net_income - dividends_paid_preferred_stock) / shares_outstanding
        
        # Free cash flow per share
        free_cash_flow_per_share = (operating_cash_flow - capex) / shares_outstanding
        
        # Dividend per share
        dividend_per_share = dividends_paid / shares_outstanding
        
        dict[year] = {
            'eps_per_share': eps_per_share,
            'free_cash_flow_per_share': free_cash_flow_per_share,
            'dividend_per_share': dividend_per_share
        }
    
    if not dict:
        return None
        
    df = pd.DataFrame.from_dict(dict, orient='index')
    df.index.name = 'fiscal_date_ending'
    df = df.apply(pd.to_numeric, errors='coerce')
    return df

# Get the dividend data
with st.spinner(f"Loading dividend data for {selected_ticker}..."):
    dividend_data = get_dividend_data(selected_ticker, year_range[0], year_range[1])

if dividend_data is None or dividend_data.empty:
    st.error(f"No dividend data available for {selected_ticker} in the selected time period.")
    st.stop()

# Display the data in a DataFrame
st.subheader(f"Dividend Sustainability Metrics for {selected_ticker}")
st.dataframe(dividend_data.round(4), use_container_width=True)

# Create the plot with Plotly
st.write("Plotting the most important metrics for dividend payments to see how well it is covered over time.")

# Reset index to make fiscal_date_ending a column
plot_data = dividend_data.reset_index()

# Create a Plotly figure
fig = px.line(plot_data, x="fiscal_date_ending", y=plot_data.columns, markers=True, title=" ")

fig.update_layout(
    xaxis_title = "Year",
    yaxis_title = "Value ($ dollars)",
    title_x = 0.5,
    height = 400
)

# Display the interactive plot
st.plotly_chart(fig, use_container_width=True)

# Calculate and display sustainability metrics
st.subheader("Dividend Payout Ratios")

# Create columns for ratios
col1, col2 = st.columns(2)

with col1:
    # Create earnings payout ratio data
    payout_ratio = (dividend_data['dividend_per_share'] / dividend_data['eps_per_share']).round(4)
    payout_ratio = payout_ratio.replace([np.inf, -np.inf], np.nan)  # Handle division by zero
    
    # Calculate average
    avg_payout = payout_ratio.mean()
    
    # Create a gauge chart for earnings payout ratio
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_payout,
        title={'text': "Earnings Payout Ratio", 'font': {'size': 24}},
        delta={'reference': 0.5, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.3], 'color': 'green'},
                {'range': [0.3, 0.6], 'color': 'yellow'},
                {'range': [0.6, 0.9], 'color': 'orange'},
                {'range': [0.9, 1], 'color': 'red'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.9
            }
        },
        number={'suffix': "%", 'valueformat': '.2%'}
    ))
    
    gauge_fig.update_layout(height=250)
    st.plotly_chart(gauge_fig, use_container_width=True)
    
    # Display historical data
    st.dataframe(pd.DataFrame(payout_ratio, columns=['Earnings Payout Ratio']), use_container_width=True)
    
    # Interpretation
    if avg_payout < 0.3:
        st.success("Low payout ratio indicates strong dividend sustainability and growth potential.")
    elif avg_payout < 0.6:
        st.info("Moderate payout ratio suggests balanced dividend policy.")
    elif avg_payout < 0.9:
        st.warning("High payout ratio may limit future dividend growth.")
    else:
        st.error("Very high payout ratio suggests potential sustainability issues.")

with col2:
    # Create FCF payout ratio data
    fcf_payout_ratio = (dividend_data['dividend_per_share'] / dividend_data['free_cash_flow_per_share']).round(4)
    fcf_payout_ratio = fcf_payout_ratio.replace([np.inf, -np.inf], np.nan)  # Handle division by zero
    
    # Calculate average
    avg_fcf_payout = fcf_payout_ratio.mean()
    
    # Create a gauge chart for FCF payout ratio
    gauge_fig2 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_fcf_payout,
        title={'text': "FCF Payout Ratio", 'font': {'size': 24}},
        delta={'reference': 0.5, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.3], 'color': 'green'},
                {'range': [0.3, 0.6], 'color': 'yellow'},
                {'range': [0.6, 0.9], 'color': 'orange'},
                {'range': [0.9, 1], 'color': 'red'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.9
            }
        },
        number={'suffix': "%", 'valueformat': '.2%'}
    ))
    
    gauge_fig2.update_layout(height=250)
    st.plotly_chart(gauge_fig2, use_container_width=True)
    
    # Display historical data
    st.dataframe(pd.DataFrame(fcf_payout_ratio, columns=['FCF Payout Ratio']), use_container_width=True)
    
    # Interpretation
    if avg_fcf_payout < 0.3:
        st.success("Low FCF payout ratio indicates very strong dividend coverage by free cash flow.")
    elif avg_fcf_payout < 0.6:
        st.info("Moderate FCF payout ratio suggests good cash flow support for dividends.")
    elif avg_fcf_payout < 0.9:
        st.warning("High FCF payout ratio suggests limited cash flow flexibility.")
    else:
        st.error("Very high FCF payout ratio indicates potential cash flow constraints.")

# Dividend Growth Analysis
st.subheader("Dividend Growth Analysis")

if len(dividend_data) > 1:
    # Get dividend growth rates
    dividend_data_reset = dividend_data.reset_index()
    dividend_data_reset['year'] = dividend_data_reset['fiscal_date_ending']
    dividend_data_reset = dividend_data_reset.sort_values('year')
    
    # Calculate year-over-year growth
    dividend_data_reset['div_growth'] = dividend_data_reset['dividend_per_share'].pct_change() * 100
    
    # Calculate CAGR
    first_year = dividend_data_reset['year'].min()
    last_year = dividend_data_reset['year'].max()
    years_diff = last_year - first_year
    first_div = dividend_data_reset[dividend_data_reset['year'] == first_year]['dividend_per_share'].values[0]
    last_div = dividend_data_reset[dividend_data_reset['year'] == last_year]['dividend_per_share'].values[0]
    
    if first_div > 0:
        cagr = ((last_div / first_div) ** (1 / years_diff) - 1) * 100
        
        # Create a growth chart
        growth_fig = go.Figure()
        
        # Add year-over-year growth bars
        growth_fig.add_trace(go.Bar(
            x=dividend_data_reset['year'][1:],
            y=dividend_data_reset['div_growth'][1:],
            name='Annual Growth',
            marker_color='lightseagreen'
        ))
        
        # Add a line for the CAGR
        growth_fig.add_trace(go.Scatter(
            x=[first_year, last_year],
            y=[cagr, cagr],
            mode='lines',
            name=f'CAGR: {cagr:.2f}%',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Update layout
        growth_fig.update_layout(
            title=f'Dividend Growth Analysis for {selected_ticker}',
            xaxis_title='Year',
            yaxis_title='Growth Rate (%)',
            template='plotly_white',
            height=400,
            yaxis=dict(ticksuffix='%'),
            hovermode='x unified'
        )
        
        st.plotly_chart(growth_fig, use_container_width=True)
        
        # Show CAGR metric
        st.metric("Dividend CAGR", f"{cagr:.2f}%")
    else:
        st.info("Cannot calculate growth rate with zero initial dividend.")
else:
    st.info("Need at least two years of data to calculate growth rates.")

# Download button for the data
csv = dividend_data.to_csv()
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name=f"{selected_ticker}_dividend_sustainability_{year_range[0]}-{year_range[1]}.csv",
    mime="text/csv",
)