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
from utils.SaveDividendData import SaveDocsData
from datetime import datetime
import atexit
from database.DatabaseConnection import db_connection

def inspect_dividend_data():
    url = 'https://www.alphavantage.co/query?function=DIVIDENDS&symbol=CCi&apikey=WYGPKB8T21WMM6LO'
    r = requests.get(url)
    data = r.json()

    print(data)

def save_dividend_paying_companies():
    save_dividend_data = SaveDocsData(DIVIDEND_SHEET_URL)
    save_dividend_data.save_data(DIVIDEND_COMPANY_FILE_PATH)
    save_dividend_data.process_data(DIVIDEND_COMPANY_FILE_PATH, FILTERED_DIVIDEND_COMPANY_FILE_PATH)

def populate_db():
    list_companies = pd.read_csv(FILTERED_DIVIDEND_COMPANY_FILE_PATH)
    list_companies = list_companies['Symbol'].tolist()
    populate = PopulateDB()
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

    current_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"./outData/companies_screened_{current_date}.xlsx"
    screener.export_results_to_excel_file(file_name)
    print(f"Screening stocks took {screening_end_time - screening_start_time} seconds")

    for ticker in all_results:
        if all_results[ticker]:
            dividend_plot = dividendAnalysis(Stock(ticker))
            try:
                dividend_plot.plot_dividend_sustainability(2013, 2023)
            except Exception as e:
                print(f"Error plotting dividend sustainability for {ticker}: {e}")

# create_excel_file()

def get_price_estimation(ticker):
    pe_ratio = PERatioEstimator(Stock(ticker))
    price_pe = pe_ratio.get_pe_ratio_estimation(2013, 2023)
    print(f"The price estimation using P/E ratio: {price_pe:.2f}$")

    ebit_price = PEBITRatioEstimator(Stock(ticker))
    price_ebit = ebit_price.get_pebit_ratio_estimation(2013, 2023)
    print(f"The price estimation using P/EBIT ratio: {price_ebit:.2f}$")

    op_cf_price = PriceOpCFRatioEstimator(Stock(ticker))
    price_op_cf = op_cf_price.get_priceOpCF_ratio_estimation(2013, 2023)
    print(f"The price estimation using P/OpCF ratio: {price_op_cf:.2f}$")

    fcf_price_estimator = PriceFCFRatioEstimator(Stock(ticker))
    price_fcf = fcf_price_estimator.get_priceFCF_ratio_estimation(2013, 2023)
    print(f"The price estimation using PEBIT ratio: {price_fcf:.2f}$")


    dividend_price_estimator = PriceDividendRatioEstimator(Stock(ticker))
    price_dividend = dividend_price_estimator.get_priceDividend_ratio_estimation(2013, 2023)
    print(f"The price estimation using P/Dividend ratio: {price_dividend:.2f}$")

    avg_price = (price_pe + price_ebit + price_op_cf + price_fcf + price_dividend) / 5

    return avg_price

print(get_price_estimation("GPC"))

atexit.register(db_connection.close_connection)