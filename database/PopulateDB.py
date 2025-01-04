from database.DatabaseCRUD import DatabaseCRUD
from stock.Stock import Stock

class PopulateDB:
    def __init__(self, db_name):
        self.db_crud = DatabaseCRUD(db_name)

    def populate_income_statement(self, list_companies):
        if list_companies is None:
            return
        for company in list_companies:
            company = Stock(company)
            df_income_statement = company.get_income_statement()
            if df_income_statement is None:
                continue
            statement_type = 'income_statement'
            ticker = company.ticker
            first_date = df_income_statement.index[0]
            company_id = self.db_crud.select_company(ticker)
            if self.db_crud.select_financial_statement(company_id, statement_type, first_date) is not None:
                continue
            for fiscalDate, row in df_income_statement.iterrows():
                self.db_crud.insert_financial_statement(ticker, statement_type, fiscalDate)
                print(f"Inserted {statement_type} for {ticker} from {fiscalDate}")
                for column in df_income_statement.columns:
                    self.db_crud.insert_financial_data(ticker, statement_type, fiscalDate, column, row[column])
                    print(f"Inserted {column} for {fiscalDate}")
            print(f"Inserted {statement_type} for {ticker}")
    
    def populate_balance_sheet(self, list_companies):
        if list_companies is None:
            return
        for company in list_companies:
            company = Stock(company)
            df_balace_sheet = company.get_balance_sheet()
            if df_balace_sheet is None:
                continue
            statement_type = 'balance_sheet'
            ticker = company.ticker
            first_date = df_balace_sheet.index[0]
            company_id = self.db_crud.select_company(ticker)
            if self.db_crud.select_financial_statement(company_id, statement_type, first_date) is not None:
                continue
            for fiscalDate, row in df_balace_sheet.iterrows():
                self.db_crud.insert_financial_statement(ticker, statement_type, fiscalDate)
                print(f"Inserted {statement_type} for {ticker} from {fiscalDate}")
                for column in df_balace_sheet.columns:
                    self.db_crud.insert_financial_data(ticker, statement_type, fiscalDate, column, row[column])
                    print(f"Inserted {column} for {fiscalDate}")
            print(f"Inserted {statement_type} for {ticker}")

    def populate_cash_flow_statement(self, list_companies):
        if list_companies is None:
            return
        for company in list_companies:
            company = Stock(company)
            df_cash_flow = company.get_cashflow_data()
            if df_cash_flow is None:
                continue
            statement_type = 'cash_flow_statement'
            ticker = company.ticker
            first_date = df_cash_flow.index[0]
            company_id = self.db_crud.select_company(ticker)
            if self.db_crud.select_financial_statement(company_id, statement_type, first_date) is not None:
                continue
            for fiscalDate, row in df_cash_flow.iterrows():
                self.db_crud.insert_financial_statement(ticker, statement_type, fiscalDate)
                print(f"Inserted {statement_type} for {ticker} from {fiscalDate}")
                for column in df_cash_flow.columns:
                    self.db_crud.insert_financial_data(ticker, statement_type, fiscalDate, column, row[column])
                    print(f"Inserted {column} for {fiscalDate}")
            print(f"Inserted {statement_type} for {ticker}")

    def populate_company_table(self, list_companies):
        if list_companies is None:
            return
        for company in list_companies:
            company = Stock(company)
            if self.db_crud.select_company(company.ticker) is not None:
                continue
            if company.yf.info['quoteType'] == 'NONE':
                sector = None
            else:
                sector = company.yf.info['sector']
            self.db_crud.insert_company(company.ticker, sector)
            print(f"Inserted {company.ticker} company from sector {sector}")

    def populate_all(self, list_companies):
        self.populate_company_table(list_companies)
        self.populate_income_statement(list_companies)
        self.populate_cash_flow_statement(list_companies)
        self.populate_balance_sheet(list_companies)


        
