from database.DatabaseCRUD import DatabaseCRUD
from stock.Stock import Stock
import datetime as dt

class PopulateDB:
    def __init__(self, db_name):
        self.db_crud = DatabaseCRUD(db_name)

    def populate_income_statement(self, list_companies):
        if list_companies is None:
            return
        for company in list_companies:
            try:
                company = Stock(company)
                statement_type = 'income_statement'
                ticker = company.ticker
                current_year = dt.datetime.now().year
                company_id = self.db_crud.select_company(ticker)

                if company_id is None:
                    print(f"Company ID not found for {ticker}")
                    continue

                if self.db_crud.select_financial_statement(company_id, statement_type, current_year - 3) > 0:
                    print(f"Skipping {statement_type} for {ticker}, already exists.")
                    continue

                df_income_statement = company.get_income_statement()
                if df_income_statement is None:
                    print(f"Income statement not retrieved for {ticker}")
                    continue

                for fiscalDate, row in df_income_statement.iterrows():
                    self.db_crud.insert_financial_statement(ticker, statement_type, fiscalDate)
                    print(f"Inserted {statement_type} for {ticker} from {fiscalDate}")
                    for column in df_income_statement.columns:
                        self.db_crud.insert_financial_data(ticker, statement_type, fiscalDate, column, row[column])
                        print(f"Inserted {column} for {fiscalDate}")
                print(f"Inserted {statement_type} for {ticker}")
            except Exception as e:
                print(f"Error processing income statement for {ticker}: {e}")
    
    def populate_balance_sheet(self, list_companies):
        if list_companies is None:
            return
        for company in list_companies:
            company = Stock(company)
            statement_type = 'balance_sheet'
            ticker = company.ticker
            current_year = dt.datetime.now().year
            company_id = self.db_crud.select_company(ticker)

            if company_id is None:
                print(f"Company ID not found for {ticker}")
                continue
            
            financial_statement_id = self.db_crud.select_financial_statement(company_id, statement_type, current_year - 3)
            if financial_statement_id > 0:
                print(f"Skipping {statement_type} for {ticker}, already exists.")
                continue
            
            df_balace_sheet = company.get_balance_sheet()
            if df_balace_sheet is None:
                print(f"Balance sheet not retrieved for {ticker}")
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
            statement_type = 'cash_flow_statement'
            ticker = company.ticker
            current_year = dt.datetime.now().year
            company_id = self.db_crud.select_company(ticker)

            if company_id is None:
                print(f"Company ID not found for {ticker}")
                continue

            if self.db_crud.select_financial_statement(company_id, statement_type, current_year - 3) > 0:
                print(f"Skipping {statement_type} for {ticker}, already exists.")
                continue

            df_cash_flow = company.get_cashflow_data()
            if df_cash_flow is None:
                print(f"Cash flow statement not retrieved for {ticker}")
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
            if self.db_crud.select_company(company.ticker) > 0:
                print(f"Company {company.ticker} is already inserted")
                continue
            if company.yf.info['quoteType'] == 'NONE':
                sector = None
            else:
                sector = company.yf.info['sector']
            self.db_crud.insert_company(company.ticker, sector)
            print(f"Inserted {company.ticker} company from sector {sector}")

    def populate_all(self, list_companies):
        # Populate company table
        try:
            self.populate_company_table(list_companies)
            print("Company table populated.")
        except Exception as e:
            print(f"Error populating company table: {e}")

        # Populate income statement
        try:
            print("Starting income statement population...")
            self.populate_income_statement(list_companies)
            print("Finished income statement population.")
        except Exception as e:
            print(f"Error populating income statements: {e}")

        # Populate cash flow statement
        # try:
        #     print("Starting cash flow statement population...")
        #     self.populate_cash_flow_statement(list_companies)
        #     print("Finished cash flow statement population.")
        # except Exception as e:
        #     print(f"Error populating cash flow statements: {e}")
        
        # # Populate balance sheet
        # try:
        #     print("Starting balance sheet population...")
        #     self.populate_balance_sheet(list_companies)
        #     print("Finished balance sheet population.")
        # except Exception as e:
        #     print(f"Error populating balance sheets: {e}")


        
