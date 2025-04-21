import streamlit as st

st.set_page_config(page_title="Stock Overview", layout="centered")

st.title("Overview")

import sys
import os
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from stock.Stock import Stock
from utils.Constants import FILTERED_DIVIDEND_COMPANY_FILE_PATH
from services.db_instance import get_db
from services.financial_data_processor import get_income_statement_df, get_balance_sheet_df, get_cashflow_statement_df
from datetime import datetime

def get_valid_defaults(defaults, available_columns):
    return [col for col in defaults if col in available_columns]

db_crud = get_db()

st.markdown("Get an overview of the stock you are interested in")

# Check if ticker is selected in session state
if 'selected_ticker' not in st.session_state or st.session_state.selected_ticker is None:
    st.warning("No company selected. Please return to the home page and select a company.")
    st.stop()

# Get the selected ticker from session state
selected_ticker = st.session_state.selected_ticker

# Display ticker in sidebar for reference
st.sidebar.info(f"Selected company: {selected_ticker}")

selected_ticker = selected_ticker.upper()

# Inițializare a stării la începutul fișierului
if "company_found" not in st.session_state:
    st.session_state.company_found = False
if "company_id" not in st.session_state:
    st.session_state.company_id = None
if "company_ticker" not in st.session_state:
    st.session_state.company_ticker = ""

if st.button("Search") and selected_ticker:
    try:
        company_id = db_crud.select_company(selected_ticker)
        if company_id is not None:
            # Verifică dacă s-a schimbat ticker-ul
            if "company_ticker" in st.session_state and st.session_state.company_ticker != selected_ticker:
                # Resetează datele financiare dacă s-a schimbat ticker-ul
                if "income_statement_df" in st.session_state:
                    del st.session_state.income_statement_df
                if "show_financial_data" in st.session_state:
                    st.session_state.show_financial_data = False

            st.session_state.company_found = True
            st.session_state.company_id = company_id
            st.session_state.company_ticker = selected_ticker
        else:
            st.session_state.company_found = False
            st.warning(f"Company **{selected_ticker.upper()}** is not stored in our database.")
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

        current_year = datetime.now().year

        if statement == 'Income Statement':
            # Verifică dacă există date pentru ticker-ul curent sau dacă trebuie reîncărcate
            if "income_statement_df" not in st.session_state:
                df = get_income_statement_df(st.session_state.company_ticker, 2009, current_year)
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
                # Inițializare dacă nu există
                if "selected_columns" not in st.session_state:
                    st.session_state.selected_columns = {}

                if "income" not in st.session_state.selected_columns:
                    st.session_state.selected_columns["income"] = ["Revenue", "Net Income"]

                valid_defaults = get_valid_defaults(st.session_state.selected_columns["income"], available_columns)

                selected_columns = st.multiselect(
                    "Select the columns for the chart: ", 
                    available_columns, 
                    default=valid_defaults)
                
                # Actualizăm session_state cu noile coloane selectate
                st.session_state.selected_columns["income"] = selected_columns

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

        elif statement == "Balance Sheet":
             # Verifică dacă există date pentru ticker-ul curent sau dacă trebuie reîncărcate
            if "balance_sheet_df" not in st.session_state:
                df = get_balance_sheet_df(st.session_state.company_ticker, 2009, current_year)
                if df is not None:
                    st.session_state.balance_sheet_df = df
                else:
                    st.warning("No financial data available")
                    st.session_state.balance_sheet_df = None
        
            # Dacă datele sunt disponibile, continuăm
            if st.session_state.balance_sheet_df is not None:
                df = st.session_state.balance_sheet_df

                st.subheader("Balance Sheet Overview")
                st.caption("📊 Values are expressed in **billion USD ($)**, rounded to 2 decimal places.")
                st.dataframe(df)

                st.markdown("---")

                # 🎚️ Selector de coloane
                available_columns = df.columns.tolist()
                if "selected_columns" not in st.session_state:
                    st.session_state.selected_columns = {}

                if "balance" not in st.session_state.selected_columns:
                    st.session_state.selected_columns["balance"] = ["Total Assets", "Total Liabilities"]

                # Filtrăm default-urile
                valid_defaults = get_valid_defaults(st.session_state.selected_columns["balance"], available_columns)
                        
                selected_columns = st.multiselect(
                    "Select the columns for the chart: ", 
                    available_columns, 
                    default=valid_defaults)
                
                # Actualizăm session_state cu noile coloane selectate
                st.session_state.selected_columns["balance"] = selected_columns

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

        elif statement == "Cashflow Statement":
            # Verifică dacă există date pentru ticker-ul curent sau dacă trebuie reîncărcate
            if "cash_flow_statement_df" not in st.session_state:
                df = get_cashflow_statement_df(st.session_state.company_ticker, 2009, current_year)
                if df is not None:
                    st.session_state.cash_flow_statement_df = df
                else:
                    st.warning("No financial data available")
                    st.session_state.cash_flow_statement_df = None
        
            # Dacă datele sunt disponibile, continuăm
            if st.session_state.cash_flow_statement_df is not None:
                df = st.session_state.cash_flow_statement_df

                st.subheader("Cash Flow Statement Overview")
                st.caption("📊 Values are expressed in **billion USD ($)**, rounded to 2 decimal places.")
                st.dataframe(df)

                st.markdown("---")

                # 🎚️ Selector de coloane
                available_columns = df.columns.tolist()
                # Inițializare dacă nu există
                if "selected_columns" not in st.session_state:
                    st.session_state.selected_columns = {}

                if "cashflow" not in st.session_state.selected_columns:
                    st.session_state.selected_columns["cashflow"] = ["Operating Cash Flow", "CAPEX"]

                valid_defaults = get_valid_defaults(st.session_state.selected_columns["cashflow"], available_columns)
                        
                selected_columns = st.multiselect(
                    "Select the columns for the chart: ", 
                    available_columns, 
                    default=valid_defaults)
                
                # Actualizăm session_state cu noile coloane selectate
                st.session_state.selected_columns["cashflow"] = selected_columns

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
            
