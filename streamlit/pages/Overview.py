import streamlit as st
import sys
import os
import sqlite3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.Constants import BASE_DIR, DB_NAME

# Find the correct database path
db_path = os.path.join(BASE_DIR, DB_NAME)

st.set_page_config(page_title="Stock Overview", layout="centered")

# Debug information
st.sidebar.write(f"Database path: {db_path}")
st.sidebar.write(f"File exists: {os.path.exists(db_path)}")

st.title("Get an overview of the stock you are interested in")

st.header("Welcome to the Stock Overview Page!")

st.markdown("""
    Please enter the stock ticker symbol you are interested in, and we will provide you with an overview of the stock's performance and key metrics.
""")

ticker = st.text_input("Enter Stock Ticker Symbol", placeholder="e.g., AAPL, MSFT, GOOGL")

if st.button("Search") and ticker:
    try:
        # Direct database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = "SELECT id FROM company WHERE UPPER(ticker) = UPPER(?)"
        cursor.execute(query, (ticker,))
        result = cursor.fetchone()
        
        if result:
            company_id = result[0]
            st.success(f"Company {ticker.upper()} found in the database!")
            
            # You can add more queries to retrieve additional company information
            # For example:
            cursor.execute("SELECT sector FROM company WHERE id = ?", (company_id,))
            company_details = cursor.fetchone()
            if company_details:
                st.write(f'Company Sector: {company_details[0]}')
        else:
            st.warning(f"Company with ticker {ticker.upper()} not found in the database.")
        
        conn.close()
    except Exception as e:
        st.error(f"Error searching for company: {str(e)}")