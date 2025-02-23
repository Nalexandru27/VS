import numpy as np
import yfinance as yf
from stock.Stock import *
import pandas as pd
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
from utils.SaveDividendData import SaveDocsData
from stock.StockScreener import StockScreener
import os
import time

import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=IBM&apikey=demo'
r = requests.get(url)
data = r.json()

print(data)

url = "https://docs.google.com/spreadsheets/d/1D4H2OoHOFVPmCoyKBVCjxIl0Bt3RLYSz/export?format=csv&gid=2128848540#gid=2128848540"
saved_csv_file_path = "outData/dividend_spreadsheet.csv"
new_csv_file_path = "outData/filtered_sorted_companies.csv"

# obj = SaveDocsData(url)
# obj.save_data(saved_csv_file_path)
# obj.process_data(saved_csv_file_path,new_csv_file_path)

# list_companies = pd.read_csv(new_csv_file_path)
# list_companies = list_companies['Symbol'].tolist()

# populate = PopulateDB('companies.db')
# populate.populate_all(list_companies)

# filtered_sorted_companies = pd.read_csv(new_csv_file_path)
# tickers = filtered_sorted_companies['Symbol'].tolist()

# current_date = datetime.now().strftime("%Y-%m-%d")
# file_name = f"./outData/companies_screened_{current_date}.xlsx"

# def create_excel_file():
#     screener = StockScreener()
#     screening_start_time = time.time()
#     all_results = {}

#     results = screener.screen_stocks(tickers)
#     all_results.update(results)

#     screening_end_time = time.time()

#     screener.result = all_results
#     screener.export_results_to_excel_file(file_name)
#     print(f"Screening stocks took {screening_end_time - screening_start_time} seconds")

#     for ticker in all_results:
#         if all_results[ticker]:
#             dividend_plot = dividendAnalysis(Stock(ticker), 'companies.db')
#             dividend_plot.plot_dividend_sustainability(2013, 2023)
    
# create_excel_file()

# def get_price_estimation(ticker):
#     pe_ratio = PERatioEstimator(Stock(ticker), 'companies.db')
#     price_pe = pe_ratio.get_pe_ratio_estimation(2012, 2023)
#     # print(f"{price_pe} is the price estimation using PE ratio")

#     ebit_price = PEBITRatioEstimator(Stock(ticker), 'companies.db')
#     price_ebit = ebit_price.get_pebit_ratio_estimation(2012, 2023)
    # print(f"{price_ebit} is the price estimation using PEBIT ratio")

    # op_cf_price = PriceOpCFRatioEstimator(Stock(ticker), 'companies.db')
    # price_op_cf = op_cf_price.get_priceOpCF_ratio_estimation(2012, 2023)
    # # print(f"{price_op_cf} is the price estimation using Price to Operating Cash Flow ratio")

    # fcf_price_estimator = PriceFCFRatioEstimator(Stock(ticker), 'companies.db')
    # price_fcf = fcf_price_estimator.get_priceFCF_ratio_estimation(2012, 2023)
    # # print(f"{price_fcf} is the price estimation using Price to Free Cash Flow ratio")

    # dividend_price_estimator = PriceDividendRatioEstimator(Stock(ticker), 'companies.db')
    # price_dividend = dividend_price_estimator.get_priceDividend_ratio_estimation(2012, 2023)
    # # print(f"{price_dividend} is the price estimation using Price to Dividend ratio")

    # avg_price = (price_pe + price_ebit + price_op_cf + price_fcf + price_dividend) / 5
    # # print(f"{avg_price} is the average price estimation")

    # return avg_price