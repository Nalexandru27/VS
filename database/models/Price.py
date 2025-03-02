import sqlite3
from datetime import datetime

class Price:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name, timeout=30, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout = 30000")
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS price(
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    close REAL NOT NULL,
                    FOREIGN KEY(company_id) REFERENCES company(id),
                    UNIQUE(company_id, date)
                );           
        """)
        self.connection.commit()

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
        if ticker is not None and self.is_valide_date(date):
            company_id = self.cursor.execute("""
                SELECT id FROM company WHERE ticker = ?                                 
            """, (ticker,)).fetchone()
            if company_id:
                return self.cursor.execute("""
                    SELECT close FROM price WHERE company_id = ? AND date = ?
                """, (company_id[0], date)).fetchone()
        return None
    
    def get_prices(self, ticker, start_date, end_date):
        if ticker is not None and self.is_valide_date(start_date) and self.is_valide_date(end_date):
            company_id = self.cursor.execute("""
                SELECT id FROM company WHERE ticker = ?                                 
            """, (ticker,)).fetchone()
            if company_id:
                return self.cursor.execute("""
                    SELECT date, close FROM price WHERE company_id = ? AND date BETWEEN ? AND ?
                """, (company_id[0], start_date, end_date)).fetchall()
        return None
    