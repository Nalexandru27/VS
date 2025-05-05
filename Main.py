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
    url = 'https://www.alphavantage.co/query?function=DIVIDENDS&symbol=GPC&apikey=WYGPKB8T21WMM6LO'
    r = requests.get(url)
    data = r.json()

    print(data)

# inspect_dividend_data()

def inspect_income_statement():
    url = 'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=NUE&apikey=WYGPKB8T21WMM6LO'
    r = requests.get(url)
    data = r.json()

    print(data)

# inspect_income_statement()

def save_dividend_paying_companies():
    save_dividend_data = SaveDocsData(DIVIDEND_SHEET_URL)
    save_dividend_data.save_data(DIVIDEND_COMPANY_FILE_PATH)
    save_dividend_data.process_data(DIVIDEND_COMPANY_FILE_PATH, FILTERED_DIVIDEND_COMPANY_FILE_PATH)

# save_dividend_paying_companies()

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

def analyze_specific_companies():
    tickers = ["TROW", "PEP", "REXR", "DEO", "HRL", "BF.B", "ARE", "RHI", "NKE", "SWKS", "TGT", "UPS", "NUE", "TTC", "O", "CBU", "OZK", "PII", "SCVL", "HPQ", "COP", "SWK", "SCL", "MDT", "WST", "MRK", "PLD", "SJW"]
    results = {}
    for ticker in tickers:
        results[ticker] = True

    screener = StockScreener()
    screener.result = results

    screener.export_results_to_excel_file("outData/specific_companies_analyzed.xlsx")

    for ticker in tickers:
        dividend_plot = dividendAnalysis(Stock(ticker))
        try:
            dividend_plot.plot_dividend_sustainability(2013, 2023)
        except Exception as e:
            print(f"Error plotting dividend sustainability for {ticker}: {e}")

atexit.register(db_connection.close_connection)
