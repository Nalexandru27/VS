import sqlite3

class FinancialData:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    def create_table(self):
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

    def insert_financial_data(self, ticker, statement_type, year, record_type, record_value):
        try:
            with self.connection:
                if record_value is not None:
                    company_id = self.cursor.execute("""
                        SELECT id FROM company WHERE ticker = ?                                 
                    """, (ticker,)).fetchone()
                    if company_id:
                        financial_statement_id = self.cursor.execute("""
                            SELECT id FROM financialStatement WHERE company_id = ? AND statement_type = ? AND year = ?
                        """, (company_id[0], statement_type, year)).fetchone()
                        if financial_statement_id:
                            self.cursor.execute("""
                                INSERT INTO financialData(financial_statement_id, record_type, record_value)
                                VALUES(?, ?, ?)
                            """, (financial_statement_id[0], record_type, record_value))
        except sqlite3.IntegrityError:
            pass

    def get_financial_data(self, ticker, statement_type, year, record_type):
        try:
            company_id = self.cursor.execute("""
                SELECT id FROM company WHERE ticker = ?                                 
            """, (ticker,)).fetchone()
            if company_id:
                financial_statement_id = self.cursor.execute("""
                    SELECT id FROM financialStatement WHERE company_id = ? AND statement_type = ? AND year = ?
                """, (company_id[0], statement_type, year)).fetchone()
                if financial_statement_id:
                    return self.cursor.execute("""
                        SELECT record_value FROM financialData WHERE financial_statement_id = ? AND record_type = ?
                    """, (financial_statement_id[0], record_type)).fetchone()
            return None
        except sqlite3.IntegrityError:
            pass

    def delete_financial_data(self, ticker, statement_type, year, record_type):
        try:
            company_id = self.cursor.execute("""
                SELECT id FROM company WHERE ticker = ?                                 
            """, (ticker,)).fetchone()
            if company_id:
                financial_statement_id = self.cursor.execute("""
                    SELECT id FROM financialStatement WHERE company_id = ? AND statement_type = ? AND year = ?
                """, (company_id[0], statement_type, year)).fetchone()
                if financial_statement_id:
                    self.cursor.execute("""
                        DELETE FROM financialData WHERE financial_statement_id = ? AND record_type = ?
                    """, (financial_statement_id[0], record_type))
        except sqlite3.IntegrityError:
            pass

    def update_financial_data(self, ticker, statement_type, year, record_type, record_value):
        try:
            if record_value is not None:
                company_id = self.cursor.execute("""
                    SELECT id FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                if company_id:
                    financial_statement_id = self.cursor.execute("""
                        SELECT id FROM financialStatement WHERE company_id = ? AND statement_type = ? AND year = ?
                    """, (company_id[0], statement_type, year)).fetchone()
                    if financial_statement_id:
                        self.cursor.execute("""
                            UPDATE financialData SET record_value = ? WHERE financial_statement_id = ? AND record_type = ?
                        """, (record_value, financial_statement_id[0], record_type))
        except sqlite3.IntegrityError:
            pass