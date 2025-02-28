from stock.Stock import *
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
import time
import datetime
from utils.Constants import DIVIDEND_SHEET_URL, DIVIDEND_COMPANY_FILE_PATH, FILTERED_DIVIDEND_COMPANY_FILE_PATH, PRICE_SHEET_URL, PRICE_HISTORY_FILE_PATH
from utils.ExportPriceHistory import ExportPriceHistory

# dividend_companies = SaveDocsData(DIVIDEND_SHEET_URL)
# dividend_companies.save_data(DIVIDEND_COMPANY_FILE_PATH)
# dividend_companies.process_data(DIVIDEND_COMPANY_FILE_PATH, FILTERED_DIVIDEND_COMPANY_FILE_PATH)

price_history = ExportPriceHistory(PRICE_SHEET_URL)
price_history.save_data(PRICE_HISTORY_FILE_PATH)

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
#     print(f"{price_pe} is the price estimation using PE ratio")

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