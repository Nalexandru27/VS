from stock.Stock import Stock
import pandas as pd
import sys, os
from utils.SafeDivide import safe_divide
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class PriceFCFRatioEstimator:
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

    # get free cash flow (computed as operating cash flow - capital expenditures) history from database for last 15 years
    def get_fcf_history(self, start_year, end_year):
        fcf_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.stock.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
            op_cf = self.stock.db_crud.select_financial_data(financial_statement_id, 'operatingCashFlow')
            if op_cf is None:
                op_cf = self.stock.db_crud.select_financial_data(financial_statement_id, 'operatingCashFow')
            capex = self.stock.db_crud.select_financial_data(financial_statement_id, 'capitalExpenditures')

            fcf_history[year] = op_cf - capex
        return fcf_history
    
    # get shares outstanding from database for last 15 years
    def get_shares_outstanding_history(self, start_year, end_year):
        shares_outstanding_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.stock.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            shares_outstanding = self.stock.db_crud.select_financial_data(financial_statement_id, 'sharesOutstanding')

            shares_outstanding_history[year] = shares_outstanding
        return shares_outstanding_history
    
    # compute operating free cash flow per share for last 15 years using free cash flow and shares outstanding (retrieved from database)
    def get_fcf_per_share_history(self, start_year, end_year):
        fcf_history = self.get_fcf_history(start_year, end_year)
        shares_outstanding_history = self.get_shares_outstanding_history(start_year, end_year)
        fcf_per_share_history = {}
        for year in range(start_year, end_year + 1):
            fcf_per_share_history[year] = safe_divide(fcf_history[year], shares_outstanding_history[year])
        return fcf_per_share_history
    
    def get_price_to_fcf_ratio_history(self, start_year, end_year):
        fcf_per_share_history = self.get_fcf_per_share_history(start_year, end_year)
        avg_year_prices = self.get_average_year_price(start_year, end_year)
        price_to_fcf_ratio_history = {}
        for year in range(start_year, end_year + 1):
            price_to_fcf_ratio_history[year] = safe_divide(avg_year_prices.loc[year], fcf_per_share_history[year])

        return price_to_fcf_ratio_history
    
    # compute average free cash flow for the last 15 years
    def get_average_price_to_FCF_ratio(self, start_year, end_year):
        price_to_fcf_ratio = self.get_price_to_fcf_ratio_history(start_year, end_year)
        if isinstance(price_to_fcf_ratio, (pd.Series, pd.DataFrame)):
            return price_to_fcf_ratio.mean()
        else:
            return safe_divide(sum(price_to_fcf_ratio.values()), len(price_to_fcf_ratio))
    
    # compute estimated price using P/FCF ratio
    # formula: Current price / (Current P/FCF ratio / Average P/FCF ratio)
    # where Current P/FCF ratio = Current price / Last FCF reported
    # if the denominator is negative, it is set to 1.5
    def get_priceFCF_ratio_estimation(self, start_year, end_year):
        latest_price = self.stock.db_crud.get_last_price(self.stock.ticker)
        
        last_fcf_per_share = self.stock.get_fcf_per_share()
        current_price_fcf_ratio = safe_divide(latest_price, last_fcf_per_share)
        
        historic_price_fcf_ratio = self.get_average_price_to_FCF_ratio(start_year, end_year)
        if isinstance(historic_price_fcf_ratio, (pd.Series, pd.DataFrame)):
            historic_price_fcf_ratio = historic_price_fcf_ratio.iloc[0]

        denominator = current_price_fcf_ratio / historic_price_fcf_ratio
        
        if denominator < 0:
            denominator = 1.5
        
        estimated_final_price = safe_divide(latest_price, denominator)

        return estimated_final_price