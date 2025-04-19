import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import atexit
from database.DatabaseConnection import db_connection
from database.DatabaseCRUD import DatabaseCRUD
from stock.StockScreener import StockScreener
from utils.Constants import FILTERED_DIVIDEND_COMPANY_FILE_PATH
from financial_analysis import financial_metrics

db_crud = DatabaseCRUD()

def get_filtered_companies():
    screener = StockScreener()
    filtered_sorted_companies = pd.read_csv(FILTERED_DIVIDEND_COMPANY_FILE_PATH)
    tickers = filtered_sorted_companies['Symbol'].tolist()
    results = screener.screen_stocks(tickers)
    passed_filters_companies = []
    for ticker, value in results.items():
        if value == True:
            passed_filters_companies.append(ticker)
    return passed_filters_companies

def create_metrics_companies_dataframe(start_year, end_year, metrics_to_calculate):
    companies = get_filtered_companies()
    all_data = []

    for ticker in companies:
        for year in range(start_year, end_year + 1):
            company_data = {'ticker': ticker, 'year': year}

            if 'MarketCap' in metrics_to_calculate:
                company_data['MarketCap'] = financial_metrics.calculate_market_cap(ticker, year)
            
            if 'CurrentRatio' in metrics_to_calculate:
                company_data['CurrentRatio'] = financial_metrics.calculate_current_ratio(ticker, year)

            if 'DividendRecord' in metrics_to_calculate:
                company_data['DividendRecord'] = financial_metrics.calculate_dividend_record(ticker, year)

            if 'DividendYield' in metrics_to_calculate:
                company_data['DividendYield'] = financial_metrics.get_dividend_yield(ticker, year)

            if 'EPS' in metrics_to_calculate:
                company_data['EPS'] = financial_metrics.calculate_EPS(ticker, year)

            if 'FCF_per_share' in metrics_to_calculate:
                company_data['FCF_per_share'] = financial_metrics.calculate_FCF_per_share(ticker, year)
            
            if 'OperatingCF_per_share' in metrics_to_calculate:
                company_data['OperatingCF_per_share'] = financial_metrics.calculate_operating_cash_flow_per_share(ticker, year)
            
            if 'OperatingIncomeMargin' in metrics_to_calculate:
                company_data['OperatingIncomeMargin'] = financial_metrics.calculate_operating_income_margin(ticker, year)
            
            if 'ROE' in metrics_to_calculate:
                company_data['ROE'] = financial_metrics.calculate_return_on_equity(ticker, year)
            
            if 'ROCE' in metrics_to_calculate:
                company_data['ROCE'] = financial_metrics.calculate_ROCE(ticker, year)
            
            if 'Debt_to_Total_Capital_Ratio' in metrics_to_calculate:
                company_data['Debt_to_Total_Capital_Ratio'] = financial_metrics.calculate_Debt_to_Total_Capital_Ratio(ticker, year)

            if 'NetIncome' in metrics_to_calculate:
                company_data['NetIncome'] = financial_metrics.get_net_income(ticker, year)

            if 'Revenue' in metrics_to_calculate:
                company_data['Revenue'] = financial_metrics.get_revenue(ticker, year)

            if 'TotalAssets' in metrics_to_calculate:
                company_data['TotalAssets'] = financial_metrics.get_total_assets(ticker, year)

            if 'TotalLiabilities' in metrics_to_calculate:
                company_data['TotalLiabilities'] = financial_metrics.get_total_liabilities(ticker, year)

            if 'TotalEquity' in metrics_to_calculate:
                company_data['TotalEquity'] = financial_metrics.get_total_equity(ticker, year)

            # Get dividend growth rate (always included)
            dividend_growth_data = financial_metrics.calculate_dividend_annual_growth_rate(ticker, start_year, end_year)
            
            if dividend_growth_data:
                growth_rate_key = year - 1
                company_data['DividendGrowthRate'] = dividend_growth_data.get(growth_rate_key)
            else:
                company_data['DividendGrowthRate'] = None

            all_data.append(company_data)

    return pd.DataFrame(all_data)

# df = create_metrics_companies_dataframe(2013,2023,['MarketCap', 'CurrentRatio', 'DividendRecord', 'DividendYield', 'EPS', 'FCF_per_share', 'OperatingCF_per_share', 'OperatingIncomeMargin', 'ROE', 'ROCE', 'Debt_to_Total_Capital_Ratio'])
# df.to_excel("dataframe_machine_learning.xlsx")

atexit.register(db_connection.close_connection)
        






