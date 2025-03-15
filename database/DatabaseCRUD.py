import sqlite3
from datetime import datetime

class DatabaseCRUD:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name, timeout=30, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout = 30000")
        self.cursor = self.connection.cursor()

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
    
    def select_no_companies(self):
        result = self.cursor.execute("""
            SELECT COUNT(*) FROM company
        """).fetchone()
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
        
    def is_valide_date(self, date):
        try:
            datetime.strptime(date, '%Y-%m-%d')
            return True
        except ValueError:
            return False
        
    def insert_price(self, ticker, date, close):
        try:
            if ticker is not None:
                with self.connection:
                    company_id = self.cursor.execute("""
                        SELECT id FROM company WHERE ticker = ?                                 
                    """, (ticker,)).fetchone()
                    if company_id and self.is_valide_date(date) and close is not None:
                        self.cursor.execute("""
                            INSERT INTO price(company_id, date, close)
                            VALUES(?, ?, ?)
                        """, (company_id[0], date, close))
        except sqlite3.IntegrityError:
            pass

    def get_price(self, ticker, date):
        try:
            if ticker is not None and self.is_valide_date(date):
                company_id = self.cursor.execute("""
                    SELECT id FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                if company_id:
                    return self.cursor.execute("""
                        SELECT close FROM price WHERE company_id = ? AND date = ?
                    """, (company_id[0], date)).fetchone()
            return None
        except sqlite3.IntegrityError:
            pass

    def get_last_price(self, ticker):
        try:
            if ticker is not None:
                company_id = self.cursor.execute("""
                    SELECT id FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                if company_id:
                    return self.cursor.execute("""
                        SELECT close FROM price WHERE company_id = ? ORDER BY date DESC LIMIT 1
                    """, (company_id[0],)).fetchone()
            return None
        except sqlite3.IntegrityError:
            pass
    
    def get_prices(self, ticker, start_date, end_date):
        try:
            if ticker is not None and self.is_valide_date(start_date) and self.is_valide_date(end_date):
                company_id = self.cursor.execute("""
                    SELECT id FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                if company_id:
                    return self.cursor.execute("""
                        SELECT date, close FROM price WHERE company_id = ? AND date BETWEEN ? AND ?
                    """, (company_id[0], start_date, end_date)).fetchall()
            return None
        except sqlite3.IntegrityError:
            pass

    def delete_price(self, ticker, date):
        try:
            if ticker is not None and self.is_valide_date(date):
                company_id = self.cursor.execute("""
                    SELECT id FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                if company_id:
                    self.cursor.execute("""
                        DELETE FROM price WHERE company_id = ? AND date = ?
                    """, (company_id[0], date))
                    self.connection.commit()
        except sqlite3.IntegrityError:
            pass
        
    def update_price(self, ticker, date, price):
        try:
            if ticker is not None and self.is_valide_date(date) and price is not None:
                company_id = self.cursor.execute("""
                    SELECT id FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                if company_id:
                    self.cursor.execute("""
                        UPDATE price SET close = ? WHERE company_id = ? AND date = ?
                    """, (price, company_id[0], date))
                    self.connection.commit()
        except sqlite3.IntegrityError:
            pass

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


