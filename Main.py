from stock.Stock import *
import sqlite3
from stock.EvalutateStock import *
from database.DatabaseCRUD import DatabaseCRUD
from database.PopulateDB import PopulateDB
from database.models.Price import Price
from HistoryAnalysis.DividendAnalysis import dividendAnalysis
from PriceEstimators.PriceEstimationEarnings import PERatioEstimator
from PriceEstimators.PriceEstimationEBIT import PEBITRatioEstimator
from PriceEstimators.PriceEstimationOpCF import PriceOpCFRatioEstimator
from PriceEstimators.PriceEstimationFCF import PriceFCFRatioEstimator
from PriceEstimators.PriceEstimationDividend import PriceDividendRatioEstimator
from utils.SaveDividendData import SaveDocsData
from stock.StockScreener import StockScreener
import time
import datetime
from utils.Constants import DIVIDEND_SHEET_URL, DIVIDEND_COMPANY_FILE_PATH, FILTERED_DIVIDEND_COMPANY_FILE_PATH, HISTORICAL_PRICE_SHEET_URL, PRICE_HISTORY_FILE_PATH, DAILY_PRICE_SHEET_URL, PRICE_DAILY_FILE_PATH
from utils.ExportPriceHistory import ExportPriceHistory
from datetime import datetime

def create_price_table():
    try:
        connection = sqlite3.connect('companies.db', timeout=30, check_same_thread=False)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout = 30000")
        cursor = connection.cursor()
        db_price = Price(connection, cursor)
        db_price.create_table()
        print("Price table created successfully")
        return True
    except Exception as e:
        print(f"Error creating price table: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def clean_price_history():
    # Citește fișierul CSV și ignoră prima coloană dacă e un index
    df = pd.read_csv("outData/PriceHistory.csv", skip_blank_lines=True, decimal=",", thousands=".", index_col=0)
    df.to_csv("outData/cleaned_PriceHistory.csv")

def print_price_history():
    df = pd.read_csv("outData/cleaned_PriceHistory.csv", index_col=0)
    print(df.iloc[:, :4])

def handling_missing_prices_history():
    df = pd.read_csv("outData/cleaned_PriceHistory.csv", index_col=0)
    available_date_percentage = (1 - df.isnull().mean()) * 100

    valid_companies = available_date_percentage[available_date_percentage >= 75].index
    df_filtered = df[valid_companies]

    df_filled = df_filtered.interpolate(method='linear', limi=5)

    still_missing = df_filled.isnull()

    df_ffill = df_filled.ffill()
    df_bfill = df_filled.bfill()

    df_filled[still_missing] = (df_ffill[still_missing] + df_bfill[still_missing]) / 2

    if df_filled.isnull().sum().sum() > 0 :
        df_filled = df_filled.fillna(df_filled.ewm(span=30).mean())

    df_filled = df_filled.fillna(df_filled.mean())

    df_filled.to_csv("outData/filled_PriceHistory.csv")

def export_price_history_to_excel():
    df = pd.read_csv("outData/filled_PriceHistory.csv", index_col=0)
    df.to_excel("outData/FilledPriceHistory.xlsx")

export_price_history_to_excel()



def save_historical_prices_into_csv():
    price_history = ExportPriceHistory(HISTORICAL_PRICE_SHEET_URL)
    price_history.save_data(PRICE_HISTORY_FILE_PATH)

def save_daily_prices_into_csv():
    daily_prices = ExportPriceHistory(DAILY_PRICE_SHEET_URL)
    daily_prices.save_data(PRICE_DAILY_FILE_PATH)

def save_dividend_paying_companies_into_csv():
    dividend_companies = SaveDocsData(DIVIDEND_SHEET_URL)
    dividend_companies.save_data(DIVIDEND_COMPANY_FILE_PATH)
    dividend_companies.process_data(DIVIDEND_COMPANY_FILE_PATH, FILTERED_DIVIDEND_COMPANY_FILE_PATH)

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

def get_alpha_data(ticker):
    url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey=43KL4PW74AWGDJZI'
    r = requests.get(url)
    data = r.json()

    print(data)