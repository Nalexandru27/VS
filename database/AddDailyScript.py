import pandas as pd
from database.PopulateDB import PopulateDB
from utils.SaveDividendData import SaveDocsData
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

url = "https://docs.google.com/spreadsheets/d/1D4H2OoHOFVPmCoyKBVCjxIl0Bt3RLYSz/export?format=csv&gid=330805790#gid=330805790"
saved_csv_file_path = "outData/dividend_spreadsheet.csv"
new_csv_file_path = "outData/filtered_sorted_companies.csv"

# obj = SaveDocsData(url)
# obj.save_data(saved_csv_file_path)
# obj.process_data(saved_csv_file_path,new_csv_file_path)

list_companies = pd.read_csv(new_csv_file_path)
list_companies = list_companies['Symbol'].tolist()

populate = PopulateDB('companies.db')
populate.populate_all(list_companies)