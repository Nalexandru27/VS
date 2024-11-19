import yfinance as yf
from Stock import *
from StockScreener import *


# screener = StockScreener()
# tickers = ['PPG']

# screener.screen_stocks(tickers)
# screener.inspect_results_of_screening()


# screener = StockScreener()
# list = ['TTC','DLB','WPC','ELV','QCOM','NUE','PPG','TGT','ARE','CWT','MKC','SWKS','NKE','WTRG']
# screener.screen_stocks(list)
# screener.export_results('results.txt')

import pandas as pd

# Load the Excel file (replace 'your_file.xlsx' with your file's name)
file_path = 'your_file.xlsx'
df = pd.read_excel(file_path)

# Extract the first column as a list
tickers = df.iloc[:, 0].tolist()

# Print the list of tickers
print(tickers)
