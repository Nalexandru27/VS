import yfinance as yf
from Stock import *
from StockScreener import *
import os
import pandas as pd
import time


current_date = datetime.now().strftime("%Y-%m-%d")
file_name = f"results_{current_date}.txt"
def create_text_file():
    if os.path.exists(FILE_PATH):
        print("File found, proceeding to read it.")
        df = pd.read_excel(FILE_PATH)
        tickers = df.iloc[:100, 0].tolist()
        screener = StockScreener()
        screening_start_time = time.time()
        screener.screen_stocks(tickers)
        screening_end_time = time.time()
        print(f"Screening time: {(screening_end_time - screening_start_time)/60:.2f} minutes")
        screener.export_results(file_name)
    else:
        print("File not found. Check the path:", FILE_PATH)
    
create_text_file()