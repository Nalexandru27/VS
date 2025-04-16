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
from stock.StockScreener import StockScreener
from utils.Constants import FILTERED_DIVIDEND_COMPANY_FILE_PATH

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

        previous_year_dividend_payout = dividend_payout_df.get(start_year)['dividendPayout']
        dividend_annual_growth_dict = {}

        for year, data in dividend_payout_df.items():
            if year == start_year:
                continue

            current_dividend_payout = data['dividendPayout']

            if current_dividend_payout is None or previous_year_dividend_payout is None:
                dividend_annual_growth = None

            if previous_year_dividend_payout != 0:
                dividend_annual_growth = round((current_dividend_payout - previous_year_dividend_payout) / previous_year_dividend_payout, 2)
                dividend_annual_growth_dict[year] = dividend_annual_growth
                previous_year_dividend_payout = current_dividend_payout

        return dividend_annual_growth_dict
    except Exception as e:
        print(f"Cannot compute dividend annual growth rate because: {e}")

dividend_annual_growth_dict = compute_dividend_annual_growth_rate("GPC", 2013, 2023)
for year, annual_growth in dividend_annual_growth_dict.items():
    print(year, annual_growth)


def get_filtered_companies():
    screener = StockScreener()

    filtered_sorted_companies = pd.read_csv(FILTERED_DIVIDEND_COMPANY_FILE_PATH)
    tickers = filtered_sorted_companies['Symbol'].tolist()

    results = screener.screen_stocks(tickers)

    passed_filters_companies = []
    for ticker, value in results.items():
        if value == True:
            passed_filters_companies.append(ticker)
    return passed_filters_companies

# def create_metrics_companies_dataframe():


import pandas as pd

data_direct_lat = {
    ('A', 2020): {'Venituri': 1000, 'Profit Net': 100, 'Active Totale': 5000},
    ('A', 2021): {'Venituri': 1100, 'Profit Net': 110, 'Active Totale': 5500},
    ('B', 2020): {'Venituri': 1500, 'Profit Net': 150, 'Active Totale': 7000},
    ('B', 2021): {'Venituri': 1600, 'Profit Net': 160, 'Active Totale': 7500},
    # ... adaugă mai multe companii și ani
}

df_direct_wide = pd.DataFrame.from_dict(data_direct_lat, orient='index')
df_direct_wide.index = pd.MultiIndex.from_tuples(df_direct_wide.index, names=['Company', 'Year'])

print(df_direct_wide)





