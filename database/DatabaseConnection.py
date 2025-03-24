# DatabaseConnection.py
import sqlite3
from threading import Lock
from utils.Constants import DB_NAME
from contextlib import contextmanager

class DatabaseConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls, db_name=DB_NAME):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseConnection, cls).__new__(cls)
                cls._instance.connection = sqlite3.connect(db_name, timeout=30, check_same_thread=False)
                cls._instance.connection.execute("PRAGMA journal_mode=WAL")
                cls._instance.connection.execute("PRAGMA busy_timeout = 30000")
        return cls._instance
    
    @contextmanager
    def get_cursor(self):
        """Returnează un cursor într-un context manager pentru a asigura închiderea corectă."""
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
            
    def commit(self):
        """Commit tranzacțiile la baza de date."""
        with self._lock:
            self.connection.commit()
            
    def close_connection(self):
        """Închide conexiunea la baza de date."""
        with self._lock:
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
                self.connection = None
            DatabaseConnection._instance = None

# Instanță globală pentru import
db_connection = DatabaseConnection()