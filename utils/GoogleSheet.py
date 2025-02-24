import gspread
from google.oauth2.service_account import Credentials
from datetime import timedelta
import datetime
import time
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

def num_to_col(n):
    """Convert a 1-indexed column number to a spreadsheet column letter string."""
    string = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

try:
    sheet = client.open(SHEET_NAME).sheet1
    print(f"Successfully opened the sheet: {SHEET_NAME}")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"Spreadsheet with name '{SHEET_NAME}' not found. Please check the name and permissions.")
    exit(1)

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

    end_date = datetime.datetime(2023,12,31)
    start_date = datetime.datetime(2013,1,1)

    num_days = (end_date - start_date).days + 1
    date_rows = [[(start_date + timedelta(days=i)).strftime('%Y-%m-%d')] for i in range(num_days)]
    sheet.update(range_name='A2', values=date_rows, value_input_option="USER_ENTERED")
    print("Date column updated successfully")

    batch_size = 60
    max_retries = 3
    for i in range(0, len(stocks), batch_size):
        batch_stocks = stocks[i:i + batch_size]
        updates = []

        for idx, stock in enumerate(batch_stocks):
            col = num_to_col(i + idx + 2)
            formula = f'=IFERROR(QUERY(GOOGLEFINANCE("{stock}"; "price"; DATE({start_date.strftime("%Y;%m;%d")}); DATE({end_date.strftime("%Y;%m;%d")}); "DAILY"); "select Col2 offset 1"; 0); "")'            
            cell_range = f'{col}2'
            updates.append({
                'range': cell_range,
                'values': [[formula]]

            })

        for retry in range(max_retries):
            try:
                sheet.batch_update(updates, value_input_option="USER_ENTERED")
                print(f"Updated batch of {len(batch_stocks)} stocks)")
                time.sleep(65)
                break
            except gspread.exceptions.APIError as batch_error:
                print(f"Batch update error: {batch_error}")
                if retry < max_retries - 1:
                    wait_time = (2 ** retry) * 60
                    print(f"Waiting {wait_time} seconds before retrying batch...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Skipping batch.")
                continue

    print("Google Sheet updated with historical price formulas!")
except gspread.exceptions.APIError as e:
    print(f"API Error occurred: {e}")
    print("Waiting 60 seconds before retrying...")
    time.sleep(65)