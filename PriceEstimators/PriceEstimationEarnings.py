from stock.Stock import Stock
from database.DatabaseCRUD import DatabaseCRUD
import pandas as pd

class PERatioEstimator:
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

    # get net income from database for last 15 years
    def get_earnings_history(self, start_year, end_year):
        net_income_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', year)
            net_income = self.db_crud.select_financial_data(financial_statement_id, 'netIncome')
            net_income_history[year] = net_income
        return net_income_history
    
    # get shares outstanding from database for last 15 years
    def get_shares_outstanding_history(self, start_year, end_year):
        shares_outstanding_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            shares_outstanding = self.db_crud.select_financial_data(financial_statement_id, 'sharesOutstanding')
            shares_outstanding_history[year] = shares_outstanding
        return shares_outstanding_history
    
    # compute EPS for last 15 years using net income and shares outstanding (retrieved from database)
    def get_earnings_per_share_history(self, start_year, end_year):
        net_income_history = self.get_earnings_history(start_year, end_year)
        shares_outstanding_history = self.get_shares_outstanding_history(start_year, end_year)
        eps_history = {}
        for year in range(start_year, end_year + 1):
            eps_history[year] = net_income_history[year] / shares_outstanding_history[year]
        return eps_history
    
    # compute P/E ratio for every year (price retrieved from yahoo finance, EPS computed with data from database)
    def get_price_to_earnings_ratio_history(self, start_year, end_year):
        annual_price_average = self.get_average_year_price(start_year, end_year)
        eps_history = self.get_earnings_per_share_history(start_year, end_year)
        pe_ratio = {}
        for year in range(start_year, end_year + 1):
            pe_ratio[year] = annual_price_average[year] / eps_history[year]
        return pe_ratio
    
    # compute average P/E ratio for the last 15 years
    def get_average_price_to_earnings_ratio_history(self, start_year, end_year):
        pe_ratio = self.get_price_to_earnings_ratio_history(start_year, end_year)
        return sum(pe_ratio.values()) / len(pe_ratio)
    
    # compute estimated price using P/E ratio
    # formula: Current price / (Current P/E ratio / Average P/E ratio)
    # where Current P/E ratio = Current price / Last EPS reported
    # if the denominator is negative, it is set to 1.5
    def get_pe_ratio_estimation(self, start_year, end_year):
        latest_price = self.db_crud.get_last_price(self.stock.ticker)
        last_eps_reported = self.stock.get_EPS()
        current_pe_ratio = latest_price / last_eps_reported
        historic_pe_ratio = self.get_average_price_to_earnings_ratio_history(start_year, end_year)
        denominator = current_pe_ratio / historic_pe_ratio
        if denominator < 0:
            denominator = 1.5
        estimated_final_price = latest_price / denominator
        return estimated_final_price
    

    




