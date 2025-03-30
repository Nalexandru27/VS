import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import Constants as cnst
from database.DatabaseCRUD import DatabaseCRUD
from database.DatabaseConnection import db_connection

def insert_daily_prices():
    df = pd.read_csv(cnst.FILLED_DAILY_PRICE_FILE_PATH, index_col=0)
    db_crud = DatabaseCRUD()
    yestarday = pd.Timestamp.today() - pd.Timedelta(days=1)
    formatted_yestarday = yestarday.strftime("%Y-%m-%d")
    for index, row in df.iterrows():
        date = formatted_yestarday
        for company, price in row.items():
            print(f"Inserting price {price} for {company} on {date}...")
            db_crud.insert_price(company, date, price)
    
    db_connection.close_connection()
    print(f"Daily prices inserted successfully into database {cnst.DB_NAME}.")

insert_daily_prices()