MIN_MARKET_CAP=2000000000
MIN_CURRENT_RATIO=2 # correct value=2
MAX_LONG_TERM_DEBT_TO_WORKING_CAPITAL_RATIO=1 # correct value=1
BILLION_DIVISION=1000000000
PE_RATIO_THRESHOLD=15 # correct value=15
EARNINGS_GROWTH_THRESHOLD=33
PRICE_TO_BOOK_RATIO=1.5 # correct value=1.5
INCREASED_DIVIDEND_RECORD=10 # correct value=20 (or 10)
PRICE_TO_BOOK_RATIO_GRAHAM=22.5 # correct value=22.5

FILE_PATH_1='D:\FacultyYear3\Licenta\Registru1.xlsx'
FILE_PATH_2='D:\FacultyYear3\Licenta\Companies to evaluate.xlsx'

SERVICE_ACCOUNT_FILE = "D:\\FacultyYear3\\Licenta\\VS\\innate-sunset-451811-f3-0c861175bff3.json"
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

DIVIDEND_SHEET_URL = "https://docs.google.com/spreadsheets/d/1D4H2OoHOFVPmCoyKBVCjxIl0Bt3RLYSz/export?format=csv&gid=2128848540#gid=2128848540"
DIVIDEND_COMPANY_FILE_PATH = "outData/dividend_company_spreadsheet.csv"
FILTERED_DIVIDEND_COMPANY_FILE_PATH = "outData/filtered_sorted_companies.csv"

HISTORICAL_PRICE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Ytd8I2ocRlYf5hyv4pH3zRhDlA7j001MIjnBpYpXkyM/export?format=csv&gid=0"
PRICE_HISTORY_FILE_PATH = "outData/Prices/PriceHistory.csv"

DAILY_PRICE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1q5nSOIf4eyAZRR3lGbH6M6aW7TcxuOXUfQ93FiJDJwg/edit?gid=0#gid=0"
PRICE_DAILY_FILE_PATH = "outData/Prices/PriceDaily.csv"