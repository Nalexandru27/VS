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

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_NAME = "Stock Price Historical Data"

def num_to_col(n):
    string = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


def wait_for_data(sheet, col, max_wait=60):
    prev_len = 0
    for _ in range(max_wait // 5):
        data_values = sheet.col_values(col)
        current_len = len(data_values)
        
        if current_len > prev_len:
            prev_len = current_len
            time.sleep(5)
        else:
            break

    return prev_len

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
    no_companies = db_crud.select_no_companies()
    print(f"Number of companies in database: {no_companies}")
    stocks = [db_crud.select_company_ticker(i) for i in range(1, no_companies + 1)]

    sheet.clear()
    header = ["Date"] + stocks
    sheet.update(range_name='A1', values=[header])
    print("Header updated successfully")
    time.sleep(1)
        
    end_date = datetime.now()
    start_date = datetime(2013, 1, 1)
        
    segments = [
        (start_date, datetime(2016, 12, 31)),
        (datetime(2017, 1, 1), datetime(2020, 12, 31)),
        (datetime(2021, 1, 1), end_date)
    ]

    date_formula = f'=IFERROR(ARRAYFORMULA(TEXT(QUERY(GOOGLEFINANCE("{stocks[0]}"; "price"; DATE({start_date.strftime("%Y;%m;%d")}); DATE({end_date.strftime("%Y;%m;%d")}); "DAILY"); "select Col1 offset 1"; 0); "YYYY-MM-DD")); "")'
            
    sheet.update(f'A2', [[date_formula]], value_input_option="USER_ENTERED")        
    time.sleep(5)

    for segment_idx, (seg_start, seg_end) in enumerate(segments):
        print(f"Processing segment {segment_idx+1}: {seg_start.strftime('%Y-%m-%d')} to {seg_end.strftime('%Y-%m-%d')}")
            
        if segment_idx == 0:
            start_row = 2
        else:
            start_row = wait_for_data(sheet, 3) + 1
            print(f"Start row for segment {segment_idx+1}: {start_row}")
            
        for idx, stock in enumerate(stocks):
            col = num_to_col(idx + 2)
                
            price_formula = f'=IFERROR(QUERY(GOOGLEFINANCE("{stock}"; "price"; DATE({seg_start.strftime("%Y;%m;%d")}); DATE({seg_end.strftime("%Y;%m;%d")}); "DAILY"); "select Col2 offset 1"; 0); "")'
                
            cell_range = f'{col}{start_row}'
            sheet.update(range_name=cell_range, values=[[price_formula]], value_input_option="USER_ENTERED")
            print(f"Added price formula for stock number {idx} - {stock} in segment {segment_idx+1}")
            time.sleep(2)
            
        print("Waiting 65 seconds for all data to be populated for the previous segment...")
        time.sleep(65)
        
    print("\nToate formulele au fost adăugate. Așteaptă ca foaia de calcul să se populeze cu date.")
    print("Acest proces poate dura câteva minute până la câteva zeci de minute, în funcție de numărul de companii.")
    print(f"URL-ul foii de calcul: {spreadsheet.url}")
        
except gspread.exceptions.APIError as e:
    print(f"API Error occurred: {e}")
    print("Waiting 60 seconds before retrying...")
    time.sleep(60)
except Exception as e:
    print(f"Error: {e}")