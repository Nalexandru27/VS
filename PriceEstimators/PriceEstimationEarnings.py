from stock.Stock import Stock
from database.DatabaseCRUD import DatabaseCRUD
import pandas as pd

class PERatioEstimator:
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

    # get net income from database for last 15 years
    def get_earnings_history(self, start_year, end_year):
        net_income_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.stock.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'income_statement', year)
            net_income = self.stock.db_crud.select_financial_data(financial_statement_id, 'netIncome')

            net_income_history[year] = net_income
        return net_income_history
    
    # get shares outstanding from database for last 15 years
    def get_shares_outstanding_history(self, start_year, end_year):
        shares_outstanding_history = {}
        for year in range(start_year, end_year + 1):
            company_id = self.stock.db_crud.select_company(self.stock.ticker)
            financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            shares_outstanding = self.stock.db_crud.select_financial_data(financial_statement_id, 'sharesOutstanding')

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
            pe_ratio[year] = annual_price_average.loc[year] / eps_history[year]

        return pe_ratio
    
    # compute average P/E ratio for the last 15 years
    def get_average_price_to_earnings_ratio_history(self, start_year, end_year):
        pe_ratio = self.get_price_to_earnings_ratio_history(start_year, end_year)
        # Verifică dacă pe_ratio este Series sau DataFrame
        if isinstance(pe_ratio, (pd.Series, pd.DataFrame)):
            # Folosește metode pandas pentru a calcula media
            return pe_ratio.mean()
        else:
            # Presupun că este un dicționar
            return sum(pe_ratio.values()) / len(pe_ratio)

    
    # compute estimated price using P/E ratio
    # formula: Current price / (Current P/E ratio / Average P/E ratio)
    # where Current P/E ratio = Current price / Last EPS reported
    # if the denominator is negative, it is set to 1.5
    def get_pe_ratio_estimation(self, start_year, end_year):
        latest_price = self.stock.db_crud.get_last_price(self.stock.ticker)
        last_eps_reported = self.stock.get_EPS()

        # Asigură-te că acestea sunt numere, nu Series
        if isinstance(latest_price, (pd.Series, pd.DataFrame)):
            latest_price = latest_price.iloc[0]
        if isinstance(last_eps_reported, (pd.Series, pd.DataFrame)):
            last_eps_reported = last_eps_reported.iloc[0]
            
        current_pe_ratio = latest_price / last_eps_reported
        historic_pe_ratio = self.get_average_price_to_earnings_ratio_history(start_year, end_year)
       
        # Asigură-te că historic_pe_ratio este un număr
        if isinstance(historic_pe_ratio, (pd.Series, pd.DataFrame)):
            historic_pe_ratio = historic_pe_ratio.iloc[0]

        denominator = current_pe_ratio / historic_pe_ratio
        
        if denominator < 0:
            denominator = 1.5
        
        estimated_final_price = latest_price / denominator
        return estimated_final_price
    

    




