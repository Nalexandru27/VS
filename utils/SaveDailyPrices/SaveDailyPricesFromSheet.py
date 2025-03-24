import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from utils.ExportPrice import ExportPrice
from utils.Constants import DAILY_PRICE_SHEET_URL, PRICE_DAILY_FILE_PATH, CLEANED_PRICE_DAILY_FILE_PATH

def save_daily_prices():
    exportPrice = ExportPrice(DAILY_PRICE_SHEET_URL)
    exportPrice.save_data(PRICE_DAILY_FILE_PATH)
    exportPrice.process_data(PRICE_DAILY_FILE_PATH, CLEANED_PRICE_DAILY_FILE_PATH)
    print(f"Daily prices saved and processed successfully to csv file {CLEANED_PRICE_DAILY_FILE_PATH}.")

save_daily_prices()