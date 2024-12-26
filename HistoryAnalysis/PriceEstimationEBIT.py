from stock.Stock import Stock
from database.DatabaseCRUD import DatabaseCRUD
import pandas as pd

class PEBITRatioEstimator:
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

    # get ebit history from database for last 15 years
    def get_ebit_history(self, start_year, end_year):
        ebit_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', year)
            ebit = self.db_crud.select_financial_data(financial_statement_id, 'ebit')
            ebit_history[year] = ebit
        return ebit_history
    
    # get shares outstanding from database for last 15 years
    def get_shares_outstanding_history(self, start_year, end_year):
        shares_outstanding_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            shares_outstanding = self.db_crud.select_financial_data(financial_statement_id, 'sharesOutstanding')
            shares_outstanding_history[year] = shares_outstanding
        return shares_outstanding_history
    
    # compute ebit per share for last 15 years using ebit and shares outstanding (retrieved from database)
    def get_ebit_per_share_history(self, start_year, end_year):
        ebit_history = self.get_ebit_history(start_year, end_year)
        shares_outstanding_history = self.get_shares_outstanding_history(start_year, end_year)
        ebit_per_share_history = {}
        for year in range(start_year, end_year + 1):
            ebit_per_share_history[year] = ebit_history[year] / shares_outstanding_history[year]
        return ebit_per_share_history
    
    def get_price_to_ebit_ratio_history(self, start_year, end_year):
        ebit = self.get_ebit_per_share_history(start_year, end_year)
        price = self.get_average_year_price(start_year, end_year)
        price_to_ebit_ratio = {}
        for year in range(start_year, end_year + 1):
            price_to_ebit_ratio[year] = price[year] / ebit[year]
        return price_to_ebit_ratio
    
    # compute average ebit for the last 15 years
    def get_average_price_to_ebit_ratio(self, start_year, end_year):
        price_to_ebit_ratio = self.get_price_to_ebit_ratio_history(start_year, end_year)
        return sum(price_to_ebit_ratio.values()) / len(price_to_ebit_ratio)
    
    # compute estimated price using P/EBIT ratio
    # formula: Current price / (Current P/EBIT ratio / Average P/EBIT ratio)
    # where Current P/EBIT ratio = Current price / Last EBIT reported
    # if the denominator is negative, it is set to 1.5
    def get_pebit_ratio_estimation(self, start_year, end_year):
        current_price = self.stock.yf.info['previousClose']
        last_ebit_reported = self.stock.yf.income_stmt.loc['EBIT'].iloc[0]
        shares_outstanding = self.stock.yf.balance_sheet.loc['Ordinary Shares Number'].iloc[0]
        last_ebit_per_share = last_ebit_reported / shares_outstanding
        current_pebit_ratio = current_price / last_ebit_per_share
        historic_pebit_ratio = self.get_average_price_to_ebit_ratio(start_year, end_year)
        denominator = current_pebit_ratio / historic_pebit_ratio
        if denominator < 0:
            denominator = 1.5
        estimated_final_price = current_price / denominator
        return estimated_final_price