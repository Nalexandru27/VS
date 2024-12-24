import numpy as np
import yfinance as yf
from stock.Stock import *
import pandas as pd
import requests
import matplotlib.pyplot as plt
from stock.EvalutateStock import *
from database.DatabaseCRUD import DatabaseCRUD
from database.PopulateDB import PopulateDB
from stock.HistoryAnalysis import historyAnalysis


companies = [Stock('GPC'), Stock('TROW'), Stock('LMT')]
lmt = Stock('LMT')
db_crud = DatabaseCRUD('companies.db')

lmt_history = historyAnalysis(Stock('LMT'), 'companies.db')
lmt_history.plot_dividend_sustainability()

# current_date = datetime.now().strftime("%Y-%m-%d")
# file_name = f"./outData/companies_screened_{current_date}.xlsx"
# def create_excel_file():
#     if os.path.exists(FILE_PATH_1):
#         print("File found, proceeding to read it.")
#         df = pd.read_excel(FILE_PATH_1)
#         data = df.iloc[1:len(df)]
#         groups = 12
#         rows = len(data)
#         prev = 0
#         screener = StockScreener()
#         for i in range(groups):
#             if i == groups - 1:
#                 next = (i + 1) * (rows // groups) + rows % groups
#             else:
#                 next = (i + 1) * (rows // groups)
#             tickers = data.iloc[prev:next, 0].tolist()
#             screening_start_time = time.time()
#             screener.screen_stocks(tickers)
#             screening_end_time = time.time()
#             prev = next
#             print(f"Screening {i+1} took: {(screening_end_time - screening_start_time)/60:.2f} minutes")
#             print(f"Sleeping for 60 seconds")
#             time.sleep(60)
#         for i in range(2):
#             print(f"Exporting in {2-i} minutes")
#             time.sleep(60)
#         screener.export_results_to_excel_file(file_name)
#     else:
#         print("File not found. Check the path:", FILE_PATH_1)
# create_excel_file()






