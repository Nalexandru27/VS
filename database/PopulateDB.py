from database.DatabaseCRUD import DatabaseCRUD
from stock.Stock import Stock
import sqlite3

class PopulateDB:
    def __init__(self, db_name):
        self.db_crud = DatabaseCRUD(db_name)

    def populate_income_statement(self, list_companies: Stock):
        if list_companies is None:
            return
        for company in list_companies:
            df_income_statement = company.get_income_statement()
            if df_income_statement is None:
                continue
            statement_type = 'income_statement'
            ticker = company.ticker
            for fiscalDate, row in df_income_statement.iterrows():
                self.db_crud.insert_financial_statement(ticker, statement_type, fiscalDate)
                print(f"Inserted {statement_type} for {ticker} from {fiscalDate}")
                for column in df_income_statement.columns:
                    self.db_crud.insert_financial_data(ticker, statement_type, fiscalDate, column, row[column])
                    print(f"Inserted {column} for {fiscalDate}")
            print(f"Inserted {statement_type} for {ticker}")
    
    def populate_balance_sheet(self, list_companies: Stock):
        if list_companies is None:
            return
        for company in list_companies:
            df_income_statement = company.get_balance_sheet()
            if df_income_statement is None:
                continue
            statement_type = 'balance_sheet'
            ticker = company.ticker
            for fiscalDate, row in df_income_statement.iterrows():
                self.db_crud.insert_financial_statement(ticker, statement_type, fiscalDate)
                print(f"Inserted {statement_type} for {ticker} from {fiscalDate}")
                for column in df_income_statement.columns:
                    self.db_crud.insert_financial_data(ticker, statement_type, fiscalDate, column, row[column])
                    print(f"Inserted {column} for {fiscalDate}")
            print(f"Inserted {statement_type} for {ticker}")

    def populate_cash_flow_statement(self, list_companies: Stock):
        if list_companies is None:
            return
        for company in list_companies:
            df_income_statement = company.get_cashflow_data()
            if df_income_statement is None:
                continue
            statement_type = 'cash_flow_statement'
            ticker = company.ticker
            for fiscalDate, row in df_income_statement.iterrows():
                self.db_crud.insert_financial_statement(ticker, statement_type, fiscalDate)
                print(f"Inserted {statement_type} for {ticker} from {fiscalDate}")
                for column in df_income_statement.columns:
                    self.db_crud.insert_financial_data(ticker, statement_type, fiscalDate, column, row[column])
                    print(f"Inserted {column} for {fiscalDate}")
            print(f"Inserted {statement_type} for {ticker}")

    def populate_company(self, list_companies: Stock):
        if list_companies is None:
            return
        for company in list_companies:
            self.db_crud.insert_company(company.ticker, company.yf.info['sector'])
            print(f"Inserted {company.ticker} company from sector {company.yf.info['sector']}")

    def populate_all(self, list_companies: Stock):
        self.populate_company(list_companies)
        self.populate_income_statement(list_companies)
        self.populate_balance_sheet(list_companies)
        self.populate_cash_flow_statement(list_companies)


        
