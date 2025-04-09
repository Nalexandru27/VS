import sqlite3
from threading import Lock
from utils.Constants import DB_NAME, BASE_DIR
import os
from contextlib import contextmanager

class DatabaseConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls, db_name=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseConnection, cls).__new__(cls)
                
                # Use the absolute path to the database
                if db_name is None:
                    db_path = os.path.join(BASE_DIR, DB_NAME)
                else:
                    db_path = db_name
                
                print(f"Connecting to database at: {db_path}")
                
                cls._instance.connection = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
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

# Reinitialize the global instance with the correct path
db_connection = DatabaseConnection()