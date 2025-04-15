import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.DatabaseCRUD import DatabaseCRUD
from database.DatabaseConnection import db_connection
import os

db_crud = DatabaseCRUD()

def get_dividend_payouts(ticker, start_year, end_year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            print(f"No company found with this ticker {ticker}")
            return None
        
        record_type = "dividendPayout"
        record_types = [record_type] if isinstance(record_type, str) else record_type
        
        dividend_payouts_df = db_crud.select_financial_data_by_year_range(
            company_id, "cash_flow_statement", start_year, end_year, record_types)
        
        if dividend_payouts_df is None:
            print(f"No data found for dividends payout for company {ticker} with id {company_id}")
            return None
        
        return dividend_payouts_df
    except Exception as e:
        print(f"Could not retrieve the dividend payouts for prediction because: {e}")

def compute_dividend_annual_growth_rate(ticker, start_year, end_year):
    try:
        dividend_payout_df = get_dividend_payouts(ticker, start_year, end_year)
        if dividend_payout_df is None:
            return None
        
        
    except Exception as e:
        print(f"Cannot compute dividend annual growth rate because: {e}")




