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
    tickers = ["TROW", "PEP", "REXR", "DEO", "HRL", "BF.B", "ARE", "RHI", "NKE", "SWKS", "TGT", "UPS", "NUE", "TTC", "O", "CBU", "OZK"]
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

def get_price_history(stock: Stock, start_year, end_year):
        start_date = f'{start_year}-01-01'
        end_date = f'{end_year}-12-31'
    
        history = stock.db_crud.get_prices(stock.ticker, start_date, end_date)
        if history is None:
            raise ValueError("No price history found for the given date range.")
       
        df_history = pd.DataFrame(history, columns=['Date', 'Close'])
       
        df_history.set_index('Date', inplace=True)
        return df_history

def get_average_year_price(stock: Stock, start_year, end_year):
        df_history = get_price_history(stock, start_year, end_year)
        df_history.index = pd.to_datetime(df_history.index)
        annual_average = df_history.groupby(df_history.index.year).mean()
        return annual_average

def get_dividends_history(stock: Stock, start_year, end_year):
        dividends_history = {}
        for year in range(start_year, end_year + 1):
            company_id = stock.db_crud.select_company(stock.ticker)
            financial_statement_id = stock.db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
            dividendPayout = stock.db_crud.select_financial_data(financial_statement_id, 'dividendPayout')
            dividends_history[year] = dividendPayout
        return dividends_history

# print("Dividends history: ", get_dividends_history(Stock("NUE"),2013,2023))
      
def get_shares_outstanding_history(stock: Stock, start_year, end_year):
        shares_outstanding_history = {}
        for year in range(start_year, end_year + 1):
            company_id = stock.db_crud.select_company(stock.ticker)
            financial_statement_id = stock.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            shares_outstanding = stock.db_crud.select_financial_data(financial_statement_id, 'sharesOutstanding')
            shares_outstanding_history[year] = shares_outstanding
        return shares_outstanding_history

# print("Shares outstanding history:", get_shares_outstanding_history(Stock("NUE"),2013,2023))

def get_dividends_per_share_history(stock: Stock, start_year, end_year):
        dividends_history = get_dividends_history(stock, start_year, end_year)
        shares_outstanding_history = get_shares_outstanding_history(stock, start_year, end_year)
        dividends_per_share_history = {}
        for year in range(start_year, end_year + 1):
            dividends_per_share_history[year] = safe_divide(dividends_history[year], shares_outstanding_history[year])
        return dividends_per_share_history

# print("Dividends per share history: ", get_dividends_per_share_history(Stock("NUE"),2013,2023))

def get_dividend_yield_history(stock: Stock, start_year, end_year):
        dividends_per_share_history = get_dividends_per_share_history(stock, start_year, end_year)
        avg_year_prices = get_average_year_price(stock, start_year, end_year)
        dividend_yield_history = {}
        for year in range(start_year, end_year + 1):
            dividend_yield_history[year] = safe_divide(dividends_per_share_history[year], avg_year_prices.loc[year])

        return dividend_yield_history

# print("Dividend yield history: ", get_dividend_yield_history(Stock("NUE"), 2013, 2023))




atexit.register(db_connection.close_connection)
