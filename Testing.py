import yfinance as yf
from Stock import *
from StockScreener import *


# screener = StockScreener()
# tickers = ['PPG']

# screener.screen_stocks(tickers)
# screener.inspect_results_of_screening()


screener = StockScreener()
list = ['TTC','DLB','WPC','ELV','QCOM','NUE','PPG','TGT','ARE','CWT','MKC','SWKS','NKE','WTRG']
screener.screen_stocks(list)
screener.inspect_results_of_screening()
