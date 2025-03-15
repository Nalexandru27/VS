import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np

class Price:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

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
        
    def bulk_insert_historical_prices_from_dataframe(self, df):
        try:
            # Resetăm indexul pentru a avea data ca o coloană
            df_reset = df.reset_index()
            
            # Asigurăm-ne că coloana Date este string în formatul 'YYYY-MM-DD'
            if pd.api.types.is_datetime64_any_dtype(df_reset['Date']):
                df_reset['Date'] = df_reset['Date'].dt.strftime('%Y-%m-%d')
            else:
                # Dacă nu este datetime, ne asigurăm că este un string și are formatul corect
                df_reset['Date'] = df_reset['Date'].astype(str)
            
            # Convertim în format long (melt)
            df_melted = df_reset.melt(
                id_vars='Date',
                var_name='ticker',
                value_name='close'
            )
            
            # Obținem dicționarul de mapare ticker -> company_id
            company_ids = {}
            with self.connection:
                self.cursor.execute("SELECT ticker, id FROM company")
                for ticker, company_id in self.cursor.fetchall():
                    company_ids[ticker] = company_id
            
            # Pregătim datele pentru inserare în bloc
            bulk_data = []
            skipped_rows = 0
            
            for _, row in df_melted.iterrows():
                ticker = row['ticker']
                date = row['Date']
                close = row['close']
                
                # Verificăm dacă valorile sunt valide
                if ticker in company_ids and self.is_valide_date(date) and close is not None and not pd.isna(close):
                    bulk_data.append((company_ids[ticker], date, float(close)))
                else:
                    skipped_rows += 1
            
            # Executăm inserarea în bloc
            if bulk_data:
                with self.connection:
                    self.cursor.executemany("""
                        INSERT OR IGNORE INTO price(company_id, date, close)
                        VALUES(?, ?, ?)
                    """, bulk_data)
            
            print(f"Rânduri procesate: {len(bulk_data)}, Rânduri ignorate: {skipped_rows}")
            return len(bulk_data)
                
        except sqlite3.Error as e:
            print(f"Eroare la inserarea în bloc: {e}")
            return 0
        except Exception as e:
            print(f"Eroare neprevăzută: {e}")
            print(f"Detalii: {str(e)}")
            return 0

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
    