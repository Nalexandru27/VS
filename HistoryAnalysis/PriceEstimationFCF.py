from stock.Stock import Stock
from database.DatabaseCRUD import DatabaseCRUD
import pandas as pd

class PriceFCFRatioEstimator:
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

    # get free cash flow (computed as operating cash flow - capital expenditures) history from database for last 15 years
    def get_fcf_history(self, start_year, end_year):
        fcf_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
            op_cf = self.db_crud.select_financial_data(financial_statement_id, 'operatingCashFlow')
            capex = self.db_crud.select_financial_data(financial_statement_id, 'capitalExpenditures')
            fcf_history[year] = op_cf - capex
        return fcf_history
    
    # get shares outstanding from database for last 15 years
    def get_shares_outstanding_history(self, start_year, end_year):
        shares_outstanding_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            shares_outstanding = self.db_crud.select_financial_data(financial_statement_id, 'sharesOutstanding')
            shares_outstanding_history[year] = shares_outstanding
        return shares_outstanding_history
    
    # compute operating free cash flow per share for last 15 years using free cash flow and shares outstanding (retrieved from database)
    def get_fcf_per_share_history(self, start_year, end_year):
        fcf_history = self.get_fcf_history(start_year, end_year)
        shares_outstanding_history = self.get_shares_outstanding_history(start_year, end_year)
        fcf_per_share_history = {}
        for year in range(start_year, end_year + 1):
            fcf_per_share_history[year] = fcf_history[year] / shares_outstanding_history[year]
        return fcf_per_share_history
    
    def get_price_to_fcf_ratio_history(self, start_year, end_year):
        fcf_per_share_history = self.get_fcf_per_share_history(start_year, end_year)
        avg_year_prices = self.get_average_year_price(start_year, end_year)
        price_to_fcf_ratio_history = {}
        for year in range(start_year, end_year + 1):
            price_to_fcf_ratio_history[year] = avg_year_prices[year] / fcf_per_share_history[year]
        return price_to_fcf_ratio_history
    
    # compute average free cash flow for the last 15 years
    def get_average_price_to_FCF_ratio(self, start_year, end_year):
        price_to_fcf_ratio = self.get_price_to_fcf_ratio_history(start_year, end_year)
        return sum(price_to_fcf_ratio.values()) / len(price_to_fcf_ratio)
    
    # compute estimated price using P/OpCF ratio
    # formula: Current price / (Current P/OpCF ratio / Average P/OpCF ratio)
    # where Current P/OpCF ratio = Current price / Last OpCF reported
    # if the denominator is negative, it is set to 1.5
    def get_priceFCF_ratio_estimation(self, start_year, end_year):
        current_price = self.stock.yf.info['previousClose']
        last_fcf_reported = self.stock.yf.cash_flow.loc['Free Cash Flow'].iloc[0]
        shares_outstanding = self.stock.yf.balance_sheet.loc['Ordinary Shares Number'].iloc[0]
        last_fcf_per_share = last_fcf_reported / shares_outstanding
        current_price_fcf_ratio = current_price / last_fcf_per_share
        historic_price_fcf_ratio = self.get_average_price_to_FCF_ratio(start_year, end_year)
        denominator = current_price_fcf_ratio / historic_price_fcf_ratio
        if denominator < 0:
            denominator = 1.5
        estimated_final_price = current_price / denominator
        return estimated_final_price