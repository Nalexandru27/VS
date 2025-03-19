import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import Constants as cnst
from database.DatabaseCRUD import DatabaseCRUD

# Rest of your code...

def fill_missing_price():
    df_daily_prices = pd.read_csv(cnst.CLEANED_PRICE_DAILY_FILE_PATH, index_col=0)
    null_columns = df_daily_prices.isnull().iloc[0]
    null_columns = null_columns[null_columns]
    companies_with_missing_prices = null_columns.index.tolist()
    print(f"Companies with missing prices: {companies_with_missing_prices}")
    df_historical_prices = pd.read_csv(cnst.FILLED_PRICE_HISTORY_FILE_PATH, index_col=0)
    companies_to_fill_missing_prices = df_historical_prices.columns.intersection(companies_with_missing_prices).tolist()
    print(f"Companies to fill missing prices: {companies_to_fill_missing_prices}")
    companies_to_drop = [company for company in companies_with_missing_prices if company not in companies_to_fill_missing_prices]
    print(f"Companies to drop: {companies_to_drop}")
    df_daily_prices = df_daily_prices.drop(columns=companies_to_drop)
    db_crud = DatabaseCRUD(cnst.DB_NAME)
    for company in companies_to_fill_missing_prices:
        lastest_price = db_crud.get_last_price(company)
        print(f"Company: {company}, Lastest price: {lastest_price}")
        df_daily_prices[company] = df_daily_prices[company].fillna(lastest_price)
    df_daily_prices.to_csv(cnst.FILLED_DAILY_PRICE_FILE_PATH)
    df_daily_prices.to_excel(cnst.FILLED_DAILY_PRICE_FILE_PATH.replace(".csv", ".xlsx"))

fill_missing_price()