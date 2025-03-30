from stock.Stock import Stock
from database.DatabaseCRUD import DatabaseCRUD
import pandas as pd
import sys, os
from utils.SafeDivide import safe_divide
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class PEBITRatioEstimator:
    def __init__(self, stock: Stock):
        self.stock = stock
        
    # get daily prices
    def get_price_history(self, start_year, end_year):
        start_date = f'{start_year}-01-01'
        end_date = f'{end_year}-12-31'
    
        history = self.stock.db_crud.get_prices(self.stock.ticker, start_date, end_date)
        if history is None:
            raise ValueError("No price history found for the given date range.")
       
        df_history = pd.DataFrame(history, columns=['Date', 'Close'])
       
        df_history.set_index('Date', inplace=True)
        return df_history

    # get price average for every year
    def get_average_year_price(self, start_year, end_year):
        df_history = self.get_price_history(start_year, end_year)
        df_history.index = pd.to_datetime(df_history.index)
        annual_average = df_history.groupby(df_history.index.year).mean()
        return annual_average

    # get ebit history from database for last 15 years
    def get_ebit_history(self, start_year, end_year):
        ebit_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.stock.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'income_statement', year)
            ebit = self.stock.db_crud.select_financial_data(financial_statement_id, 'ebit')

            ebit_history[year] = ebit
        return ebit_history
    
    # get shares outstanding from database for last 15 years
    def get_shares_outstanding_history(self, start_year, end_year):
        shares_outstanding_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.stock.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            shares_outstanding = self.stock.db_crud.select_financial_data(financial_statement_id, 'sharesOutstanding')

            shares_outstanding_history[year] = shares_outstanding
        return shares_outstanding_history
    
    # compute ebit per share for last 15 years using ebit and shares outstanding (retrieved from database)
    def get_ebit_per_share_history(self, start_year, end_year):
        ebit_history = self.get_ebit_history(start_year, end_year)
        shares_outstanding_history = self.get_shares_outstanding_history(start_year, end_year)
        ebit_per_share_history = {}
        for year in range(start_year, end_year + 1):
            ebit_per_share_history[year] = safe_divide(ebit_history[year], shares_outstanding_history[year])
        return ebit_per_share_history
    
    def get_price_to_ebit_ratio_history(self, start_year, end_year):
        ebit = self.get_ebit_per_share_history(start_year, end_year)
        price = self.get_average_year_price(start_year, end_year)
        price_to_ebit_ratio = {}
        for year in range(start_year, end_year + 1):
            price_to_ebit_ratio[year] = safe_divide(price.loc[year], ebit[year])

        return price_to_ebit_ratio
    
    # compute average ebit for the last 15 years
    def get_average_price_to_ebit_ratio(self, start_year, end_year):
        price_to_ebit_ratio = self.get_price_to_ebit_ratio_history(start_year, end_year)
        if isinstance(price_to_ebit_ratio, (pd.Series, pd.DataFrame)):
            return price_to_ebit_ratio.mean()
        else:
            return safe_divide(sum(price_to_ebit_ratio.values()), len(price_to_ebit_ratio))

    
    # compute estimated price using P/EBIT ratio
    # formula: Current price / (Current P/EBIT ratio / Average P/EBIT ratio)
    # where Current P/EBIT ratio = Current price / Last EBIT reported
    # if the denominator is negative, it is set to 1.5
    def get_pebit_ratio_estimation(self, start_year, end_year):
        latest_price = self.stock.db_crud.get_last_price(self.stock.ticker)
        
        company_id = self.stock.db_crud.select_company(self.stock.ticker)

        income_statement_id = self.stock.db_crud.select_financial_statement(company_id, "income_statement", end_year)
        last_ebit_reported = self.stock.db_crud.select_financial_data(income_statement_id, "ebit")
        
        balance_sheet_id = self.stock.db_crud.select_financial_statement(company_id, "balance_sheet", end_year)
        shares_outstanding = self.stock.db_crud.select_financial_data(balance_sheet_id, "sharesOutstanding")
        
        last_ebit_per_share = safe_divide(last_ebit_reported, shares_outstanding)
        current_pebit_ratio = safe_divide(latest_price,last_ebit_per_share)
        
        historic_pebit_ratio = self.get_average_price_to_ebit_ratio(start_year, end_year)
        
        if isinstance(historic_pebit_ratio, (pd.Series, pd.DataFrame)):
            historic_pebit_ratio = historic_pebit_ratio.iloc[0]

        denominator = current_pebit_ratio / historic_pebit_ratio
        if denominator < 0:
            denominator = 1.5
        estimated_final_price = safe_divide(latest_price, denominator)
        
        return estimated_final_price