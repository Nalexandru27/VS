import sqlite3

class DatabaseCRUD:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name, timeout=30, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout = 30000")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS company(
                    id INTEGER PRIMARY KEY,
                    ticker TEXT NOT NULL UNIQUE,
                    sector TEXT
                );           
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS financialStatement(
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    statement_type TEXT NOT NULL ,
                    year INTEGER NOT NULL,
                    FOREIGN KEY(company_id) REFERENCES companyd(id),
                    UNIQUE(company_id, statement_type, year)
                );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS financialData(
                    id INTEGER PRIMARY KEY,
                    financial_statement_id INTEGER NOT NULL,
                    record_type TEXT NOT NULL,
                    record_value NUMERIC NOT NULL,
                    FOREIGN KEY(financial_statement_id) REFERENCES financialStatement(id),
                    UNIQUE(financial_statement_id, record_type)
                );
        """)

        self.connection.commit()

    def insert_company(self, ticker, sector):
        try:
            with self.connection:
                self.cursor.execute("""
                    INSERT INTO company(ticker, sector)
                    VALUES(?, ?)
                """, (ticker, sector))
        except sqlite3.IntegrityError:
            pass

    def insert_financial_statement(self, ticker, statement_type, year):
        try:
            with self.connection:
                company_id = self.cursor.execute("""
                    SELECT id FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                if company_id:
                    self.cursor.execute("""
                        INSERT INTO financialStatement(company_id, statement_type, year)
                        VALUES(?, ?, ?)
                    """, (company_id[0], statement_type, year))
        except sqlite3.IntegrityError:
            pass  # Ignore duplicate entries

    def insert_financial_data(self, ticker, statement_type, year, record_type, record_value):
        try:
            with self.connection:
                # get the company id
                company_id = self.cursor.execute("""SELECT id FROM company WHERE ticker = ?
                """, (ticker,)).fetchone()

                # if company exists get the company id
                if company_id:
                    # get the financial statement id in which I want to insert the record
                    financial_statement_id = self.cursor.execute("""
                        SELECT id FROM financialStatement WHERE company_id = ? AND statement_type = ? AND year = ?
                    """, (company_id[0], statement_type, year)).fetchone()

                # if financial statement exists insert the financial data into it
                if financial_statement_id:
                    self.cursor.execute("""
                        INSERT INTO financialData(financial_statement_id, record_type, record_value)
                        VALUES(?, ?, ?)
                    """, (financial_statement_id[0], record_type, record_value))
        except sqlite3.IntegrityError:
            pass  # Ignore duplicate entries

    def select_company(self, ticker):
        return self.cursor.execute("""
            SELECT * FROM company WHERE ticker = ?                                 
        """,(ticker)).fetchone()
    
    def select_financial_statement(self, company_id, statement_type, year):
        return self.cursor.execute("""
            SELECT * FROM financialStatement WHERE company_id = ? and statement_type = ? and year = ?
        """, (company_id, statement_type, year)).fetchone()
    
    def select_financial_data(self, financial_statement_id, record_type):
        return self.cursor.execute("""
            SELECT * FROM financialData WHERE financial_statement_id = ? and record_type = ?
        """, (financial_statement_id, record_type)).fetchone()

    def close(self):
        self.cursor.close()
        self.connection.close()


