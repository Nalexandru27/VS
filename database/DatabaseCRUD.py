import sqlite3
from datetime import datetime
from database.DatabaseConnection import db_connection
from threading import Lock

class DatabaseCRUD:
    def __init__(self):
        self.connection = db_connection
        self._lock = Lock()

    def insert_company(self, ticker, sector):
        try:
            with self._lock, self.connection.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO company(ticker, sector)
                    VALUES(?, ?)
                """, (ticker, sector))
                self.connection.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return self.select_company(ticker)

    def insert_financial_statement(self, ticker, statement_type, year):
        try:
            with self._lock, self.connection.get_cursor() as cursor:
                company_id = self.select_company(ticker)
                if company_id:
                    cursor.execute("""
                        INSERT INTO financialStatement(company_id, statement_type, year)
                        VALUES(?, ?, ?)
                    """, (company_id[0], statement_type, year))
                    self.connection.commit()
                    return cursor.lastrowid
        except sqlite3.IntegrityError:
            return self.select_financial_statement(company_id, statement_type, year)

    def insert_financial_data(self, ticker, statement_type, year, record_type, record_value):
        try:
            with self._lock, self.connection.get_cursor() as cursor:
                # get the company id
                company_id = self.select_company(ticker)

                # if company exists
                if company_id:
                    # get the financial statement id in which I want to insert the record
                    cursor.execute("""
                        SELECT id FROM financialStatement WHERE company_id = ? AND statement_type = ? AND year = ?
                    """, (company_id[0], statement_type, year))
                    financial_statement_id = cursor.fetchone()

                # if financial statement exists insert the financial data into it
                if financial_statement_id:
                    cursor.execute("""
                        INSERT INTO financialData(financial_statement_id, record_type, record_value)
                        VALUES(?, ?, ?)
                    """, (financial_statement_id[0], record_type, record_value))
                    self.connection.commit()
                    return cursor.lastrowid
        except sqlite3.IntegrityError:
            pass  # Ignore duplicate entries

    def select_company(self, ticker):
            self.connection.commit()
            ticker = ticker.strip()  # Elimină spațiile
            with self.connection.get_cursor() as cursor:
                query = "SELECT id FROM company WHERE UPPER(ticker) = UPPER(?)"
                # print(f"Executing: {query} with ticker={ticker}")
                cursor.execute(query, (ticker,))
                result = cursor.fetchone()
                # print(f"Result: {result}")

                if result is None:
                    print(f"No company found with ticker '{ticker}'")
                    print(f"Căutare pentru: UPPER('{ticker}') = {ticker.upper()}")
                    return None
                return result[0]
    
    def select_company_ticker(self, company_id):
        with self.connection.get_cursor() as cursor:
            cursor.execute("""
                SELECT ticker FROM company WHERE id = ?
            """, (company_id,))
            result = cursor.fetchone()

            if result is None:
                return None
            return result[0]
    
    def select_company_sector(self, ticker):
        with self.connection.get_cursor() as cursor:
            cursor.execute("""
                SELECT sector FROM company WHERE ticker = ?
            """, (ticker,))
            result = cursor.fetchone()

            if result is None:
                return None
            return result[0]
    
    def select_no_companies(self):
        with self.connection.get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM company
            """)
            result = cursor.fetchone()
           
            if result is None:
                return None
            return result[0]
    
    def select_financial_statement(self, company_id, statement_type, year):
        with self.connection.get_cursor() as cursor:
            query = "SELECT id FROM financialStatement WHERE company_id = ? and statement_type = ? and year = ?"
            # print(f"Executing: {query} with company_id={company_id}")
            cursor.execute(query, (company_id, statement_type, year))
            result = cursor.fetchone()
            # print(f"Result: {result}")
            if result is None:
                return None
            return result[0]
    
    def select_financial_data(self, financial_statement_id, record_type):
        with self.connection.get_cursor() as cursor:
            query = "SELECT record_value FROM financialData WHERE financial_statement_id = ? and record_type = ?"
            # print(f"Executing: {query} with financial_statement_id={financial_statement_id}")
            cursor.execute(query, (financial_statement_id, record_type))
            result = cursor.fetchone()
            # print(f"Result: {result}")
            if result is None:
                return None
            return result[0]
    
    def rename_column(self, old_column_name, new_column_name):
        """Rename a column in financialData table by updating record_type values"""
        try:
            with self._lock, self.connection.get_cursor() as cursor:
                # Check if old column exists
                check_query = """
                    SELECT COUNT(*) FROM financialData 
                    WHERE record_type = ?
                """
                count = cursor.execute(check_query, (old_column_name,)).fetchone()[0]
                
                if count == 0:
                    print(f"Warning: No records found with record_type '{old_column_name}'")
                    return
                    
                # Update the record_type
                update_query = """
                    UPDATE financialData 
                    SET record_type = ?
                    WHERE record_type = ?
                """
                cursor.execute(update_query, (new_column_name, old_column_name))
                self.connection.commit()
                print(f"Successfully renamed {count} records from '{old_column_name}' to '{new_column_name}'")
                return count
                
        except sqlite3.Error as e:
            print(f"Error renaming column: {e}")
            self.connection.rollback()
            return None
        
    def is_valid_date(self, date):
        try:
            datetime.strptime(date, '%Y-%m-%d')
            return True
        except ValueError:
            return False
        
    def insert_price(self, ticker, date, close):
        try:
            if ticker is not None:
                with self._lock, self.connection.get_cursor() as cursor:
                    company_id = self.select_company(ticker)
                    if company_id and self.is_valid_date(date) and close is not None:
                        cursor.execute("""
                            INSERT INTO price(company_id, date, close)
                            VALUES(?, ?, ?)
                        """, (company_id, date, close))
                        self.connection.commit()
                        return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_price(self, ticker, date):
        try:
            if ticker is not None and self.is_valid_date(date):
                with self.connection.get_cursor() as cursor:
                    company_id = self.select_company(ticker)
                    if company_id:
                        cursor.execute("""
                            SELECT close FROM price WHERE company_id = ? AND date = ?
                        """, (company_id, date))
                        result = cursor.fetchone()

                        if result is None:
                            return None
                        return result[0]
            return None
        except sqlite3.IntegrityError as e:
            print(f"Error getting price: {e}")
            return None

    def get_last_price(self, ticker):
        try:
            if ticker is None or ticker == "None":
                return None
            with self.connection.get_cursor() as cursor:
                company_id = self.select_company(ticker)
                if company_id is None or company_id == "None":
                    return None
                else:
                    query = "SELECT close FROM price WHERE company_id = ? ORDER BY date DESC LIMIT 1"
                    # print(f"Executing: {query} with ticker={ticker}")
                    cursor.execute(query, (company_id,))
                    result = cursor.fetchone()
                    # print(f"Result: {result}")
                    if result is None:
                        return None
                    return result[0]
            return None
        except sqlite3.Error as e:
            print(f"Error getting last price: {e}")
            return None
    
    def get_prices(self, ticker, start_date, end_date):
        try:
            if ticker is not None and self.is_valid_date(start_date) and self.is_valid_date(end_date):
                with self.connection.get_cursor() as cursor:
                    company_id = self.select_company(ticker)
                    if company_id:
                        cursor.execute("""
                            SELECT date, close FROM price WHERE company_id = ? AND date BETWEEN ? AND ?
                        """, (company_id, start_date, end_date))
                        return cursor.fetchall()
            return None
        except sqlite3.Error as e:
            print(f"Error getting prices: {e}")
            return None

    def delete_price(self, ticker, date):
        try:
            if ticker is not None and self.is_valid_date(date):
                with self._lock, self.connection.get_cursor() as cursor:
                    company_id = self.select_company(ticker)
                    if company_id:
                        cursor.execute("""
                            DELETE FROM price WHERE company_id = ? AND date = ?
                        """, (company_id, date))
                        self.connection.commit()
                        return True
            return False
        except sqlite3.Error as e:
            print(f"Error deleting price: {e}")
            self.connection.rollback()
            return False
        
    def update_price(self, ticker, date, price):
        try:
            if ticker is not None and self.is_valid_date(date) and price is not None:
                with self._lock, self.connection.get_cursor() as cursor:
                    company_id = self.select_company(ticker)
                    if company_id:
                        cursor.execute("""
                            UPDATE price SET close = ? WHERE company_id = ? AND date = ?
                        """, (price, company_id, date))
                        self.connection.commit()
                        return True
            return False
        except sqlite3.Error as e:
            print(f"Error updating price: {e}")
            self.connection.rollback()
            return False

    def change_value(self, table_name, column_name, old_value, new_value):
        try:
            with self._lock, self.connection.get_cursor() as cursor:
                # Evită SQL injection folosind parametrii pentru numele tabelului și coloanei
                safe_tables = ['company', 'financialStatement', 'financialData', 'price']
                
                if table_name not in safe_tables:
                    print(f"Error: Table '{table_name}' not allowed for safety reasons")
                    return False
                    
                query = f"UPDATE {table_name} SET {column_name} = ? WHERE {column_name} = ?"
                cursor.execute(query, (new_value, old_value))
                self.connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error changing value: {e}")
            self.connection.rollback()
            return False

    def delete_company(self, ticker):
        try:
            with self._lock, self.connection.get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM company WHERE ticker = ?
                """, (ticker,))
                self.connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error deleting company: {e}")
            self.connection.rollback()
            return False

    def delete_all_financial_statement(self):
        try:
            with self._lock, self.connection.get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM financialStatement
                """)
                self.connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error deleting all financial statements: {e}")
            self.connection.rollback()
            return False

    def delete_all_financial_data(self):
        try:
            with self._lock, self.connection.get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM financialData
                """)
                self.connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error deleting all financial data: {e}")
            self.connection.rollback()
            return False


