import sqlite3

class Company:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS company(
                    id INTEGER PRIMARY KEY,
                    ticker TEXT NOT NULL UNIQUE,
                    sector TEXT
                );           
        """)

        self.connection.commit()

    def insert_company(self, ticker, sector):
        try:
            if ticker is not None and sector is not None:
                with self.connection:
                    self.cursor.execute("""
                        INSERT INTO company(ticker, sector)
                        VALUES(?, ?)
                    """, (ticker, sector))
        except sqlite3.IntegrityError:
            pass

    def select_company_id(self, ticker):
        try:
            if ticker is not None:
                result = self.cursor.execute("""
                    SELECT id FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                
                if result is None:
                    print(f"No company found with ticker '{ticker}'")
                    return None
            return result[0]
        except sqlite3.IntegrityError:
            pass

    def select_company_ticker(self, company_id):
        try:
            if company_id is not None:
                result = self.cursor.execute("""
                    SELECT ticker FROM company WHERE id = ?                                 
                """, (company_id,)).fetchone()
                
                if result is None:
                    print(f"No company found with id '{company_id}'")
                    return None
            return result[0]
        except sqlite3.IntegrityError:
            pass

    def select_company_sector(self, ticker):
        try:
            if ticker is not None:
                result = self.cursor.execute("""
                    SELECT sector FROM company WHERE ticker = ?                                 
                """, (ticker,)).fetchone()
                if result is None:
                    print(f"No company found with ticker '{ticker}'")
                    return None
                return result[0]
        except sqlite3.IntegrityError:
            pass

    def delete_company(self, ticker):
        try:
            if ticker is not None:
                self.cursor.execute("""
                    DELETE FROM company WHERE ticker = ?
                """, (ticker,))
                self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def update_company(self, ticker, sector):
        try:
            if ticker is not None and sector is not None:
                self.cursor.execute("""
                    UPDATE company SET sector = ? WHERE ticker = ?
                """, (sector, ticker))
                self.connection.commit()
        except sqlite3.IntegrityError:
            pass

    def get_no_of_companies(self):
        try:
            return self.cursor.execute("""
                SELECT COUNT(*) FROM company
            """).fetchone()[0]
        except sqlite3.IntegrityError:
            pass
        
        