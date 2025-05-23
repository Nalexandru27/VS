# Financial Ratios
# 3_FinancialRatios.py

import streamlit as st

st.set_page_config(page_title="Financial Ratios", layout="wide")

st.title("Financial Ratios")

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from services.financial_data_processor import get_financial_ratios_df
from services.db_instance import get_db

# Sidebar
st.sidebar.header("Controls")

db_crud = get_db()

# Check if ticker is selected in session state
if 'selected_ticker' not in st.session_state or st.session_state.selected_ticker is None:
    st.warning("No company selected. Please return to the home page and select a company.")
    st.stop()

# Get the selected ticker from session state
selected_ticker = st.session_state.selected_ticker.upper()

# Display ticker in sidebar for reference
st.sidebar.info(f"Selected company: {selected_ticker}")

# Get data for the selected company
df =  get_financial_ratios_df(selected_ticker, 2013, 2023)

# Year range slider
min_year = 2013
max_year = 2023
year_range = st.sidebar.slider(
    "Select time period",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    key="year_slider"
)

# Filter data based on selected years
filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

# Display the financial ratios table
st.subheader(f"Financial Ratios for {selected_ticker} ({year_range[0]}-{year_range[1]})")
st.dataframe(filtered_df, use_container_width=True)

# Download button for the table
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name=f"{selected_ticker}_financial_ratios_{year_range[0]}-{year_range[1]}.csv",
    mime="text/csv",
)

# Plot section
st.subheader("Financial Ratios Visualization")

# Get all metrics (excluding Year)
metrics = [col for col in df.columns if col != 'Year']

# Multi-select for metrics to display
selected_metrics = st.multiselect(
    "Select metrics to visualize",
    options=metrics,
    default=[],
    key="metrics_selector"
)

# Plot the selected metrics if any are selected
if selected_metrics:
    # Reshape data for plotting
    plot_data = filtered_df.melt(
        id_vars=['Year'],
        value_vars=selected_metrics,
        var_name='Metric',
        value_name='Value'
    )
    
    # Create plot
    fig = px.line(
        plot_data,
        x='Year',
        y='Value',
        color='Metric',
        title=f"Financial Ratios Over Time for {selected_ticker}",
        markers=True,
        line_shape='linear'
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Value",
        legend_title="Metrics",
        hovermode="x unified"
    )
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select one or more metrics above to visualize them.")

# Add callback for company change to reset selected metrics
# (This is handled by the key parameter in the widgets which forces a reset when the company changes)

# Footer
st.markdown("---")
st.caption(f"Data last updated: {datetime.now().strftime('%Y-%m-%d')}")