import streamlit as st
import sys
import os
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from stock.Stock import Stock
from utils.Constants import BASE_DIR, DB_NAME, FILTERED_DIVIDEND_COMPANY_FILE_PATH
from services.db_instance import get_db
from services.financial_data_processor import get_income_statement_df
from datetime import datetime

st.set_page_config(page_title="Stock Overview", layout="centered")

db_crud = get_db()

# Find the correct database path
db_path = os.path.join(BASE_DIR, DB_NAME)

# Debug information
st.sidebar.write(f"Database path: {db_path}")
st.sidebar.write(f"File exists: {os.path.exists(db_path)}")

st.title("Get an overview of the stock you are interested in")

st.header("Welcome to the Stock Overview Page!")

st.markdown("""
    Please enter the stock ticker symbol you are interested in, and we will provide you with an overview of the stock's performance and key metrics.
""")

ticker = st.text_input("Enter Stock Ticker Symbol", placeholder="e.g., AAPL, MSFT, GOOGL")
ticker = ticker.upper()

# Inițializare a stării la începutul fișierului
if "company_found" not in st.session_state:
    st.session_state.company_found = False
if "company_id" not in st.session_state:
    st.session_state.company_id = None
if "company_ticker" not in st.session_state:
    st.session_state.company_ticker = ""

if st.button("Search") and ticker:
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is not None:
            st.session_state.company_found = True
            st.session_state.company_id = company_id
            st.session_state.company_ticker = ticker
        else:
            st.session_state.company_found = False
            st.warning(f"Company **{ticker.upper()}** is not stored in our database.")
    except Exception as e:
        st.error(f"Error searching for company: {str(e)}")

# Afișăm date doar dacă compania a fost găsită
if st.session_state.company_found:
    st.success(f"Company **{st.session_state.company_ticker.upper()}** was found in the database.")
    company_sector = db_crud.select_company_sector(st.session_state.company_ticker)
    stock = Stock(st.session_state.company_ticker)
    dividend_record = stock.get_dividend_record_from_excel(FILTERED_DIVIDEND_COMPANY_FILE_PATH)
    marketcap = stock.get_market_cap()
    last_price = db_crud.get_last_price(st.session_state.company_ticker)
    balance_sheet_id = None
    current_year = datetime.now().year
    marketcap_billions = round(int(marketcap) / 1_000_000_000, 2) if isinstance(marketcap, (int, float)) else "N/A"
    st.write(f"This company does business in the sector of {company_sector} and has increased its dividends for {dividend_record} years consecutively. Now {st.session_state.company_ticker} stands for a marketcap of around {marketcap_billions} billions $.") 
    st.write(f"Latest close price per share was: {last_price}$")
    statement = st.selectbox(
        'Please select a financial statement',
        ('Income Statement', 'Balance Sheet', 'Cashflow Statement')
    )
    st.write('You selected: ', statement)

    if "show_financial_data" not in st.session_state:
        st.session_state.show_financial_data = False

    if st.button("Show Financial Overview") or st.session_state.show_financial_data:
        st.session_state.show_financial_data = True

        if statement == 'Income Statement':
            if "income_statement_df" not in st.session_state:
                df = get_income_statement_df(st.session_state.company_ticker, 2009, 2025)
                if df is not None:
                    st.session_state.income_statement_df = df
                else:
                    st.warning("No financial data available")
                    st.session_state.income_statement_df = None

            # Dacă datele sunt disponibile, continuăm
            if st.session_state.income_statement_df is not None:
                df = st.session_state.income_statement_df

                st.subheader("Income Statement Overview")
                st.caption("📊 Values are expressed in **billion USD ($)**, rounded to 2 decimal places.")
                st.dataframe(df)

                st.markdown("---")

                # 🎚️ Selector de coloane
                available_columns = df.columns.tolist()
                if "selected_columns" not in st.session_state:
                    st.session_state.selected_columns = ["Revenue", "Net Income"]
                        
                selected_columns = st.multiselect(
                    "Select the columns for the chart: ", 
                    available_columns, 
                    default=st.session_state.selected_columns)
                
                # Actualizăm session_state cu noile coloane selectate
                st.session_state.selected_columns = selected_columns

                # 📈 Tip de grafic
                chart_type = st.radio("Choose the chart type: ", ["Bar Chart", "Line Chart"])

                if selected_columns:
                    fig_data = df[selected_columns].reset_index() # resetăm indexul ca să avem 'Year' ca coloană
                    
                    for col in selected_columns:
                        if chart_type == "Bar Chart":
                                fig = px.bar(fig_data, x="Year", y=col, title=f"{col} - Bar Chart")
                        else:
                            fig = px.line(fig_data, x="Year", y=col, markers=True, title=f"{col} - Line Chart")

                        fig.update_layout(
                            xaxis_title = "Year",
                            yaxis_title = "Value (billions USD)",
                            title_x = 0.5,
                            height = 400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Select at least one column to generate a chart.")
            else:
                st.warning("No financial data available")
