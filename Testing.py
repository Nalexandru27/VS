import yfinance as yf
from Stock import *
from StockScreener import *


screener = StockScreener()
tickers = ['TGT']

screener.screen_stocks(tickers)
screener.inspect_results_of_screening()

