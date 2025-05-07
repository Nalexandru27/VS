from sec_edgar_downloader import Downloader
import pandas as pd
import time
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.DatabaseCRUD import DatabaseCRUD

db_crud = DatabaseCRUD()

dl = Downloader("nastasealexandru01@gmail.com","./sec_edgar_fillings")

companies_ticker = db_crud.select_all_company_tickers()

for ticker in ["GPC", "ADM", "TGT"]:
    try:
        dl.get("10-K", ticker, limit=1, download_details=True)
        print(f"Downloaded 10-K for {ticker}")
        time.sleep(1.5)
    except Exception as e:
        print(f"Error downloading 10-K for {ticker}: {e}")