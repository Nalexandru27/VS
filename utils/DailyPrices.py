import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from database.DatabaseCRUD import DatabaseCRUD
from Constants import SERVICE_ACCOUNT_FILE, SCOPES

current_year = datetime.today().year

MARKET_HOLIDAYS = {
    f"{current_year}-01-01", f"{current_year}-01-20", f"{current_year}-02-17", f"{current_year}-05-26",
    f"{current_year}-07-04", f"{current_year}-09-01", f"{current_year}-10-09", f"{current_year}-11-11",
    f"{current_year}-11-27", f"{current_year}-12-25"
}

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_NAME = "Stock Price Daily"

def num_to_col(n):
    string = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

try:
    try:
        spreadsheet = client.open(SHEET_NAME)
        sheet = spreadsheet.sheet1
        print(f"Successfully opened the sheet: {SHEET_NAME}")
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create(SHEET_NAME)
        sheet = spreadsheet.sheet1
        print(f"Created new spreadsheet: {SHEET_NAME}")
    
    db_name = os.path.join(parent_dir, "companies.db")
    db_crud = DatabaseCRUD(db_name)
    no_companies = int(db_crud.select_no_companies())
    print(f"Number of companies in database: {no_companies}")
    stocks = [db_crud.select_company_ticker(i) for i in range(1, no_companies - 695)]

    sheet.clear()
    header = ["Date"] + stocks
    sheet.update(range_name='A1', values=[header])
    print("Header updated successfully")
    time.sleep(1)

    today = datetime.today().strftime("%Y-%m-%d")
    weekday = datetime.today().weekday()

    if weekday in [5, 6] or today in MARKET_HOLIDAYS:
        print(f"{today} is a non-trading day. Exiting script.")
        exit()
    else:
        print(f"{today} the markets are open. We add prices into the sheet.")
        sheet.insert_row(index=2, values=[today])

        print(f"Updating price for {today}...")

        for idx, stock in enumerate(stocks):
            col = num_to_col(idx + 2)
            today = datetime.today().strftime("%Y;%m;%d")
            price_formula = f'=IFERROR(QUERY(GOOGLEFINANCE("{stock}"; "price"; DATE({today})); "select Col2 offset 1"; 0); "")'
            cell_range = f'{col}{2}'
            sheet.update(range_name=cell_range, values=[[price_formula]], value_input_option="USER_ENTERED")
            print(f"Added price formula for {stock}, waiting 2 seconds...")
            time.sleep(2)
        print("Prices updated successfully for all stocks")
        
        print("\nWait for 60 seconds until all formulas was introduced and the file populated with all the prices.")
        time.sleep(60)
        print("This process is complete.")
        print(f"Spreadsheet URL: {spreadsheet.url}")
        
except gspread.exceptions.APIError as e:
    print(f"API Error occurred: {e}")
    print("Waiting 60 seconds before retrying...")
    time.sleep(60)
except Exception as e:
    print(f"Error: {e}")