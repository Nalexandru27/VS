from stock.Stock import Stock
from database.DatabaseCRUD import DatabaseCRUD
import pandas as pd

class PriceDividendRatioEstimator:
    def __init__(self, stock: Stock, db_name):
        self.stock = stock
        self.db_crud = DatabaseCRUD(db_name)

    # get daily prices from yahoo finance
    def get_price_history(self, start_year, end_year):
        start_date = f'{start_year}-01-01'
        end_date = f'{end_year}-12-31'
        history = self.stock.yf.history(start=start_date, end=end_date, interval='1d')
        history = history['Close']
        history.index = pd.to_datetime(history.index)
        history.index.name = 'Date'
        return history

    # get price average for every year
    def get_average_year_price(self, start_year, end_year):
        history = self.get_price_history(start_year, end_year)
        annual_average = history.groupby(history.index.year).mean()
        annual_average.index.name = 'Year'
        return annual_average

    # get dividends paid history from database for last 15 years
    def get_dividends_history(self, start_year, end_year):
        dividends_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
            dividendPayout = self.db_crud.select_financial_data(financial_statement_id, 'dividendPayout')
            dividends_history[year] = dividendPayout
        return dividends_history
    
    # get shares outstanding from database for last 15 years
    def get_shares_outstanding_history(self, start_year, end_year):
        shares_outstanding_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            shares_outstanding = self.db_crud.select_financial_data(financial_statement_id, 'sharesOutstanding')
            shares_outstanding_history[year] = shares_outstanding
        return shares_outstanding_history
    
    # compute dividend payout per share for last 15 years using dividend payout and shares outstanding (retrieved from database)
    def get_dividends_per_share_history(self, start_year, end_year):
        dividends_history = self.get_dividends_history(start_year, end_year)
        shares_outstanding_history = self.get_shares_outstanding_history(start_year, end_year)
        dividends_per_share_history = {}
        for year in range(start_year, end_year + 1):
            dividends_per_share_history[year] = dividends_history[year] / shares_outstanding_history[year]
        return dividends_per_share_history
    
    # get dividend yield for last 15 years
    def get_dividend_yield_history(self, start_year, end_year):
        dividends_per_share_history = self.get_dividends_per_share_history(start_year, end_year)
        avg_year_prices = self.get_average_year_price(start_year, end_year)
        dividend_yield_history = {}
        for year in range(start_year, end_year + 1):
            dividend_yield_history[year] = dividends_per_share_history[year] / avg_year_prices[year]
        return dividend_yield_history
    
    # compute average dividends paid for the last 15 years
    def get_average_price_to_dividends_yields(self, start_year, end_year):
        dividends_yield = self.get_dividend_yield_history(start_year, end_year)
        return sum(dividends_yield.values()) / len(dividends_yield)
    
    # compute estimated price using P/Dividend ratio
    # formula: Current price / (Historic yield / Current yield)
    # where Current P/Dividend ratio = Current price / Last Dividend reported
    # if the denominator is negative, it is set to 1.5
    def get_priceDividend_ratio_estimation(self, start_year, end_year):
        latest_price = self.db_crud.get_last_price(self.stock.ticker)

        historic_price_dividend_yield = self.get_average_price_to_dividends_yields(start_year, end_year)

        company_id = self.db_crud.select_company(self.stock.ticker)
        cash_flow_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', end_year)
        last_dividend_payout = self.db_crud.select_financial_data(cash_flow_statement_id, 'dividendPayout')

        balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', end_year)
        shares_outstanding = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')

        last_dividendPayout_per_share = last_dividend_payout / shares_outstanding
        current_dividend_yield = last_dividendPayout_per_share / latest_price 

        denominator = historic_price_dividend_yield / current_dividend_yield
        if denominator < 0:
            denominator = 1.5
        estimated_final_price = latest_price / denominator
        return estimated_final_price