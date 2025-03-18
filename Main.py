from stock.Stock import *
from stock.EvalutateStock import *
from database.PopulateDB import PopulateDB
from HistoryAnalysis.DividendAnalysis import dividendAnalysis
from PriceEstimators.PriceEstimationEarnings import PERatioEstimator
from PriceEstimators.PriceEstimationEBIT import PEBITRatioEstimator
from PriceEstimators.PriceEstimationOpCF import PriceOpCFRatioEstimator
from PriceEstimators.PriceEstimationFCF import PriceFCFRatioEstimator
from PriceEstimators.PriceEstimationDividend import PriceDividendRatioEstimator
from stock.StockScreener import StockScreener
import time, datetime
from utils.Constants import DIVIDEND_SHEET_URL, DIVIDEND_COMPANY_FILE_PATH, FILTERED_DIVIDEND_COMPANY_FILE_PATH, HISTORICAL_PRICE_SHEET_URL, PRICE_HISTORY_FILE_PATH, DAILY_PRICE_SHEET_URL, PRICE_DAILY_FILE_PATH, CLEANED_PRICE_DAILY_FILE_PATH
from utils.ExportPrice import ExportPrice
from datetime import datetime

def save_daily_prices_into_csv():
    daily_prices = ExportPrice(DAILY_PRICE_SHEET_URL)
    daily_prices.save_data(PRICE_DAILY_FILE_PATH)
    daily_prices.process_data(PRICE_DAILY_FILE_PATH, CLEANED_PRICE_DAILY_FILE_PATH)

def print_daily_prices():
    df = pd.read_csv(CLEANED_PRICE_DAILY_FILE_PATH, index_col=0)
    null_columns = df.isnull().iloc[0]
    null_columns = null_columns[null_columns]
    print(null_columns.index.tolist())

print_daily_prices()

def populate_db():
    list_companies = pd.read_csv(FILTERED_DIVIDEND_COMPANY_FILE_PATH)
    list_companies = list_companies['Symbol'].tolist()
    populate = PopulateDB('companies.db')
    populate.populate_all(list_companies)

def create_excel_file():
    current_date = datetime.now().strftime("%Y-%m-%d")

    screener = StockScreener()
    screening_start_time = time.time()
    all_results = {}

    filtered_sorted_companies = pd.read_csv(FILTERED_DIVIDEND_COMPANY_FILE_PATH)
    tickers = filtered_sorted_companies['Symbol'].tolist()

    results = screener.screen_stocks(tickers)
    all_results.update(results)

    screening_end_time = time.time()

    screener.result = all_results

    current_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"./outData/companies_screened_{current_date}.xlsx"
    screener.export_results_to_excel_file(file_name)
    print(f"Screening stocks took {screening_end_time - screening_start_time} seconds")

    for ticker in all_results:
        if all_results[ticker]:
            dividend_plot = dividendAnalysis(Stock(ticker), 'companies.db')
            dividend_plot.plot_dividend_sustainability(2013, 2023)

def get_price_estimation(ticker):
    pe_ratio = PERatioEstimator(Stock(ticker), 'companies.db')
    price_pe = pe_ratio.get_pe_ratio_estimation(2012, 2023)
    print(f"{price_pe} is the price estimation using PE ratio")

    ebit_price = PEBITRatioEstimator(Stock(ticker), 'companies.db')
    price_ebit = ebit_price.get_pebit_ratio_estimation(2012, 2023)
    print(f"{price_ebit} is the price estimation using PEBIT ratio")

    op_cf_price = PriceOpCFRatioEstimator(Stock(ticker), 'companies.db')
    price_op_cf = op_cf_price.get_priceOpCF_ratio_estimation(2012, 2023)

    fcf_price_estimator = PriceFCFRatioEstimator(Stock(ticker), 'companies.db')
    price_fcf = fcf_price_estimator.get_priceFCF_ratio_estimation(2012, 2023)

    dividend_price_estimator = PriceDividendRatioEstimator(Stock(ticker), 'companies.db')
    price_dividend = dividend_price_estimator.get_priceDividend_ratio_estimation(2012, 2023)

    avg_price = (price_pe + price_ebit + price_op_cf + price_fcf + price_dividend) / 5

    return avg_price