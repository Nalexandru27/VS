import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from database.DatabaseCRUD import DatabaseCRUD

SERVICE_ACCOUNT_FILE = "D:\\FacultyYear3\\Licenta\\VS\\innate-sunset-451811-f3-0c861175bff3.json"
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_NAME = "Stock Price Historical Data"

try:
    sheet = client.open(SHEET_NAME).sheet1
    print(f"Successfully opened the sheet: {SHEET_NAME}")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"Spreadsheet with name '{SHEET_NAME}' not found. Please check the name and permissions.")
    exit(1)

end_date = datetime.now()
start_date = end_date - timedelta(days=15*365)

start_date_str = start_date.strftime("%Y;%m;%d")
end_date_str = end_date.strftime("%Y;%m;%d")

print(f"Fetching price data from {start_date_str} to {end_date_str}...")

db_name = os.path.join(parent_dir, "companies.db")

db_crud = DatabaseCRUD(db_name)

no_companies = db_crud.select_no_companies()
print(f"Number of companies in database: {no_companies}")

stocks = []
for i in range(1, no_companies + 1):
    ticker = db_crud.select_company_ticker(i)
    stocks.append(ticker)

try:
    sheet.clear()
    print("Sheet cleared successfully")
    time.sleep(1)

    header = ["Date"] + stocks
    sheet.update(values=[header], range_name='A1')
    print("Header updated successfully")
    time.sleep(1)

    batch_size = 60
    for i in range(0, len(stocks), batch_size):
        batch_stocks = stocks[i:i + batch_size]
        updates = []
        
        for idx, stock in enumerate(batch_stocks):
            col = chr(65 + idx + 1)
            formula = f'=INDEX(GOOGLEFINANCE("{stock}"; "price"; DATE({start_date_str}); DATE({end_date_str}); "DAILY");;2)'
            cell_range = f'{col}2'
            updates.append({
                'range': cell_range,
                'values': [[formula]]
            })
        
        try:
            sheet.batch_update(updates)
            print(f"Updated batch of {len(batch_stocks)} stocks (columns A to {chr(65 + len(batch_stocks) - 1)})")
            time.sleep(65)
        except gspread.exceptions.APIError as batch_error:
            print(f"Batch update error: {batch_error}")
            time.sleep(65)
            continue

    print("Google Sheet updated with historical price formulas!")
except gspread.exceptions.APIError as e:
    print(f"API Error occurred: {e}")
    print("Waiting 60 seconds before retrying...")
    time.sleep(65)