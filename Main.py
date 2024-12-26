import numpy as np
import yfinance as yf
from stock.Stock import *
import pandas as pd
import requests
import matplotlib.pyplot as plt
from stock.EvalutateStock import *
from database.DatabaseCRUD import DatabaseCRUD
from database.PopulateDB import PopulateDB
from HistoryAnalysis.DividendAnalysis import dividendAnalysis
from PriceEstimators.PriceEstimationEarnings import PERatioEstimator
from PriceEstimators.PriceEstimationEBIT import PEBITRatioEstimator
from PriceEstimators.PriceEstimationOpCF import PriceOpCFRatioEstimator
from PriceEstimators.PriceEstimationFCF import PriceFCFRatioEstimator
from PriceEstimators.PriceEstimationDividend import PriceDividendRatioEstimator

companies = [Stock('GPC'), Stock('TROW'), Stock('LMT')]
lmt = Stock('LMT')
db_crud = DatabaseCRUD('companies.db')
ticker = 'GPC'

pe_ratio = PERatioEstimator(Stock(ticker), 'companies.db')
price_pe = pe_ratio.get_pe_ratio_estimation(2009, 2023)
print(f"{price_pe} is the price estimation using PE ratio")

ebit_price = PEBITRatioEstimator(Stock(ticker), 'companies.db')
price_ebit = ebit_price.get_pebit_ratio_estimation(2009, 2023)
print(f"{price_ebit} is the price estimation using PEBIT ratio")

op_cf_price = PriceOpCFRatioEstimator(Stock(ticker), 'companies.db')
price_op_cf = op_cf_price.get_priceOpCF_ratio_estimation(2009, 2023)
print(f"{price_op_cf} is the price estimation using Price to Operating Cash Flow ratio")

fcf_price_estimator = PriceFCFRatioEstimator(Stock(ticker), 'companies.db')
price_fcf = fcf_price_estimator.get_priceFCF_ratio_estimation(2009, 2023)
print(f"{price_fcf} is the price estimation using Price to Free Cash Flow ratio")

dividend_price_estimator = PriceDividendRatioEstimator(Stock(ticker), 'companies.db')
price_dividend = dividend_price_estimator.get_priceDividend_ratio_estimation(2009, 2023)
print(f"{price_dividend} is the price estimation using Price to Dividend ratio")

avg_price = (price_pe + price_ebit + price_op_cf + price_fcf + price_dividend) / 5
print(f"{avg_price} is the average price estimation")

# lmt_history = dividendAnalysis(Stock('LMT'), 'companies.db')
# lmt_history.plot_dividend_sustainability()

gpc_history = dividendAnalysis(Stock(ticker), 'companies.db')
gpc_history.plot_dividend_sustainability(2009, 2023)

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






