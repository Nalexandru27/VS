import yfinance as yf
from Stock import *
from StockScreener import *
import os
import pandas as pd
import time

file_path = 'D:\FacultyYear3\Licenta\Registru1.xlsx'

def create_text_file(file_path, file_name):
    if os.path.exists(file_path):
        print("File found, proceeding to read it.")
        df = pd.read_excel(file_path)
        tickers = df.iloc[:, 0].tolist()
        screener = StockScreener()
        screening_start_time = time.time()
        screener.screen_stocks(tickers)
        screening_end_time = time.time()
        print(f"Screening time: {(screening_end_time - screening_start_time)/60:.2f} minutes")
        screener.export_results(file_name)
    else:
        print("File not found. Check the path:", file_path)
    
create_text_file(file_path, 'results.txt')
    