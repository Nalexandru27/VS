import streamlit as st
import sys
import os
from sqlite3 import OperationalError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database.DatabaseCRUD import DatabaseCRUD

st.set_page_config(page_title="Stock Overview", layout="centered")

st.title("Get an overview of the stock you are interested in")

st.header("Welcome to the Stock Overview Page!")

st.markdown("""
    Please enter the stock ticker symbol you are interested in, and we will provide you with an overview of the stock's performance and key metrics.
""")

ticker = st.text_input("Enter Stock Ticker Symbol", placeholder="e.g., AAPL, MSFT, GOOGL")

if st.button("Search") and ticker:
    db_crud = DatabaseCRUD()

    try:
        company_id = db_crud.select_company(ticker)
        if company_id is not None:
            st.success(f"Company {ticker} found in the database!")
        else:
            st.warning(f"Company {ticker} not found in the database.")
    except OperationalError as e:
        if "no such table" in str(e):
            st.error("Database setup incomplete. The company table doesn't exist yet.")
            st.info("Please make sure to initialize your database with the required tables first.")
        else:
            st.error(f"Database error: {str(e)}")