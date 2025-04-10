import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pandas as pd
import Constants as cnst
from database.DatabaseCRUD import DatabaseCRUD
from database.DatabaseConnection import db_connection
from utils.GoogleDriveDB import upload_file_to_drive, download_file_from_drive, list_files_in_folder

database_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "companies.db"))

def insert_daily_prices():
    # Listează fișierele pentru debugging
    print("Verificăm fișierele din folderul Google Drive:")
    files = list_files_in_folder()
    
    # Afișează calea exactă unde se va descărca baza de date
    print(f"Calea pentru descărcare: {os.path.abspath(database_path)}")
    
    # Afișează numele exact al fișierului de backup căutat
    backup_filename = "backup_" + cnst.DB_NAME
    print(f"Căutăm fișierul: {backup_filename}")

    df = pd.read_csv(cnst.FILLED_DAILY_PRICE_FILE_PATH, index_col=0)
    if download_file_from_drive("backup_" + cnst.DB_NAME, database_path):
        print(f"Latest database version of {cnst.DB_NAME} was downloaded successfully at {database_path}")
        time.sleep(20)
        db_crud = DatabaseCRUD()
        yestarday = pd.Timestamp.today() - pd.Timedelta(days=1)
        formatted_yestarday = yestarday.strftime("%Y-%m-%d")
        for index, row in df.iterrows():
            date = formatted_yestarday
            for company, price in row.items():
                print(f"Inserting price {price} for {company} on {date}...")
                db_crud.insert_price(company, date, price)
        
        db_connection.close_connection()
        print(f"Daily prices inserted successfully into database {cnst.DB_NAME}.")

        time.sleep(10)
        upload_file_to_drive(database_path, cnst.DB_NAME)
        print(f"Updated database {cnst.DB_NAME} was successfully uploaded to Google Drive")
    else:
        print(f"Error when tried to download latest database version of {cnst.DB_NAME} from google drive")

insert_daily_prices()