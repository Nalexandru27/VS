import sqlite3

class DatabaseCRUD:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name, timeout=30, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout = 30000")
        self.cursor = self.connection.cursor()

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
            result = self.cursor.execute("""
                SELECT id FROM company WHERE ticker = ?                                 
            """, (ticker,)).fetchone()
            
            if result is None:
                print(f"No company found with ticker '{ticker}'")
                return None
            return result[0]
    
    def select_company_ticker(self, company_id):
        result = self.cursor.execute("""
            SELECT ticker FROM company WHERE id = ?
        """, (company_id,)).fetchone()
        if result is None:
            return None
        return result[0]
    
    def select_company_sector(self, ticker):
        result = self.cursor.execute("""
            SELECT sector FROM company WHERE ticker = ?
        """, (ticker,)).fetchone()
        if result is None:
            return None
        return result[0]
    
    def select_financial_statement(self, company_id, statement_type, year):
        result = self.cursor.execute("""
            SELECT id FROM financialStatement WHERE company_id = ? and statement_type = ? and year = ?
        """, (company_id, statement_type, year)).fetchone()
        if result is None:
            return None
        return result[0]
    
    def select_financial_data(self, financial_statement_id, record_type):
        result = self.cursor.execute("""
            SELECT record_value FROM financialData WHERE financial_statement_id = ? and record_type = ?
        """, (financial_statement_id, record_type)).fetchone()
        if result is None:
            return None
        return result[0]
    
    def rename_column(self, old_column_name, new_column_name):
        """Rename a column in financialData table by updating record_type values"""
        try:
            with self.connection:
                # Check if old column exists
                check_query = """
                    SELECT COUNT(*) FROM financialData 
                    WHERE record_type = ?
                """
                count = self.cursor.execute(check_query, (old_column_name,)).fetchone()[0]
                
                if count == 0:
                    print(f"Warning: No records found with record_type '{old_column_name}'")
                    return
                    
                # Update the record_type
                update_query = """
                    UPDATE financialData 
                    SET record_type = ?
                    WHERE record_type = ?
                """
                self.cursor.execute(update_query, (new_column_name, old_column_name))
                self.connection.commit()
                
                print(f"Successfully renamed {count} records from '{old_column_name}' to '{new_column_name}'")
                
        except sqlite3.Error as e:
            print(f"Error renaming column: {e}")
            self.connection.rollback()
            return

    def change_value(self, table_name, column_name, old_value, new_value):
        query = f"UPDATE {table_name} SET {column_name} = ? WHERE {column_name} = ?"
        self.cursor.execute(query, (new_value, old_value))
        self.connection.commit()
    
    def delete_company(self, ticker):
        self.cursor.execute("""
            DELETE FROM company WHERE ticker = ?
        """, (ticker,))
        self.connection.commit()

    def delete_all_financial_statement(self):
        self.cursor.execute("""
            DELETE FROM financialStatement
        """)
        self.connection.commit()

    def delete_all_financial_data(self):
        self.cursor.execute("""
            DELETE FROM financialData
        """)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()


