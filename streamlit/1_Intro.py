# Intro
# 1_Intro.py

import streamlit as st
st.set_page_config(page_title="Financial Analysis Dashboard", layout="wide")

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.db_instance import get_db

st.title("Fundamental Stock Analysis Application")

st.header("Welcome to the Stock Analysis App!")

st.markdown("""
    This application allows you to analyze stocks that have a record of paying and increasing their dividends each year.
    We have a database of over 650 stocks for which you can find the following information:
    - Income Statement
    - Balance Sheet
    - Cash Flow Statement
    - Daily Price
            
    Based on this information, you can perform various analyses, including:
    - Dividend Sustainability
    - Financial Ratios
    - Price Estimations
    - Chart Analysis
            
    Welcome to the world of stock analysis!
""")

# Initialize session state for selected ticker
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None

db_crud = get_db()

# Get all tickers from database
all_tickers = db_crud.select_all_company_tickers()

# Create sidebar for ticker selection
st.sidebar.header("Company Selection")

# Search and select ticker
search_term = st.sidebar.text_input("Search ticker:")

# Filter tickers based on search
if not search_term:
    # Show first 5 tickers if search is empty
    filtered_tickers = all_tickers[:5]
else:
    # Filter by search term
    search_upper = search_term.upper()
    filtered_tickers = [ticker for ticker in all_tickers if ticker.startswith(search_upper)]

# Display filtered tickers in a selectbox
if filtered_tickers:
    options_with_placeholder = ["Select a company..."] + filtered_tickers

    selected_option = st.sidebar.selectbox(
        "Select ticker:",
        options=options_with_placeholder,
        index=0
    )

# Salvează doar dacă nu e placeholder-ul
if selected_option != "Select a company...":
    st.session_state.selected_ticker = selected_option
else:
    st.session_state.selected_ticker = None


# Main content
if st.session_state.get("selected_ticker"):
    st.header(f"Company: {st.session_state.selected_ticker}")
    
    # Navigation instructions
    st.info("👈 Use the sidebar navigation to explore different analysis pages for this company.")
else:
    st.info("👈 Please select a company ticker from the sidebar to begin analysis.")

