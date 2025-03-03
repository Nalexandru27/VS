import sqlite3

class FinancialStatement:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS financialStatement(
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    statement_type TEXT NOT NULL ,
                    year INTEGER NOT NULL,
                    FOREIGN KEY(company_id) REFERENCES company(id),
                    UNIQUE(company_id, statement_type, year)
                );
        """)
        self.connection.commit()

    def insert_financial_statement(self, ticker, statement_type, year):
        try:
            with self.connection:
                if statement_type is not None and year is not None:
                    company_id = self.cursor.execute("""
                        SELECT id FROM company WHERE ticker = ?                                 
                    """, (ticker,)).fetchone()
                    if company_id:
                        self.cursor.execute("""
                            INSERT INTO financialStatement(company_id, statement_type, year)
                            VALUES(?, ?, ?)
                        """, (company_id[0], statement_type, year))
        except sqlite3.IntegrityError:
            pass

    def get_financial_statement(self, company_id, statement_type, year):
        try:
            if company_id is not None and statement_type is not None and year is not None:
                result = self.cursor.execute("""
                    SELECT id FROM financialStatement WHERE company_id = ? AND statement_type = ? AND year = ?
                """, (company_id, statement_type, year)).fetchone()
                if result is None:
                    print(f"No financial statement found with company_id '{company_id}', statement_type '{statement_type}', year '{year}'")
                    return None
                return result[0]
        except sqlite3.IntegrityError:
            pass