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

# url = 'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=ARE&apikey=43KL4PW74AWGDJZI'
# r = requests.get(url)
# data = r.json()
# annual_income = data['annualReports'][0]
# print(annual_income)

# url = 'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol=ARE&apikey=43KL4PW74AWGDJZI'
# r = requests.get(url)
# data = r.json()
# annual_balance = data['annualReports'][0]
# print(annual_balance)

# url = 'https://www.alphavantage.co/query?function=CASH_FLOW&symbol=IBM&apikey=demo'
# r = requests.get(url)
# data = r.json()
# annual_cash = data['annualReports'][0]

# companies = [Stock('GPC'), Stock('TROW'), Stock('LMT')]
# lmt = Stock('LMT')
# db_crud = DatabaseCRUD('companies.db')
# ticker = 'GPC'

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

# gpc_history = dividendAnalysis(Stock(ticker), 'companies.db')
# gpc_history.plot_dividend_sustainability(2009, 2023)

# tickers = ['TROW', 'MRK', 'AMT', 'CCI', 'REXR', 'AMD', 'ZTS', 'MDLZ', 'PEP', 'NEU', 'NNN', 'INTC', 'DEO', 'HSY', 'ADBE', 'BAH', 'DHI', 'LFUS', 'SWKS', 'NKE', 'ARE', 'GPC', 'ADM', 'AWK', 'HII', 'UPS', 'WTRG', 'TGT', 'TTC', 'PII']
# db_crud = DatabaseCRUD('companies.db')
# screener = StockScreener()
# results = screener.screen_stocks(tickers)
# screener.export_results_to_excel_file('outData/screened_companies.xlsx')


db_crud = DatabaseCRUD('companies.db')
tickers = []
for i in range(1, 512):
    ticker = db_crud.select_company_ticker(i)
    tickers.append(ticker)

def chunk_list(list, no_chunks):
    chunk_size = len(list) // no_chunks
    return [list[i * chunk_size:(i+1) * chunk_size] for i in range(no_chunks - 1)] + [list[(no_chunks - 1) * chunk_size:]]

current_date = datetime.now().strftime("%Y-%m-%d")
file_name = f"./outData/companies_screened_{current_date}.xlsx"

def create_excel_file():
    screener = StockScreener()
    screening_start_time = time.time()
    all_results = {}

    chunks = chunk_list(tickers, 5)

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1} out of {len(chunks)}")
        results = screener.screen_stocks(chunk)
        all_results.update(results)
        time.sleep(60)
        
    screening_end_time = time.time()

    screener.result = all_results
    screener.export_results_to_excel_file(file_name)
    print(f"Screening stocks took {screening_end_time - screening_start_time} seconds")
    
create_excel_file()

# stock = yf.Ticker('IOSP')
# print(stock.info)
# print(stock.income_stmt)
# print(stock.balance_sheet)
# print(stock.financials.index)
# print(stock.cashflow.index)

