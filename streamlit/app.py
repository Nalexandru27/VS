import streamlit as st
st.set_page_config(page_title="Stock Analysis", layout="centered")

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