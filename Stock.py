from datetime import datetime
import requests
import yfinance as yf
from Tresholds import *

def convert_to_billion(value):
    return int(value) / BILLION_DIVISION

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)

    # TEST 1
    # Market Capitalization > 2 billion & using yahoo finance
    def get_market_cap(self):
        return self.stock.info['marketCap']

    def check_market_cap(self):
        return self.stock.info['marketCap'] >= MIN_MARKET_CAP
    
    # TEST 2.1
    # Current Ratio >= 2 & using yahoo finance
    def get_current_ratio(self):
        return self.stock.info['currentRatio']

    def check_current_ratio(self):
        return self.stock.info['currentRatio'] >= MIN_CURRENT_RATIO
    
    # TEST 2.2
    # Long-Term Debt to Working Capital Ratio <= 1 & using yahoo finance
    def calculate_LTDebt_to_WC(self):
        balance_sheet = self.stock.balance_sheet
        current_assets = balance_sheet.loc["Current Assets"].iloc[0]
        current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0]
        working_capital = current_assets - current_liabilities
        long_term_debt = balance_sheet.loc["Long Term Debt"].iloc[0]
        return long_term_debt / working_capital
    
    def check_LTDebt_To_WC(self):
        LTDebtToWC = self.calculate_LTDebt_to_WC()
        return (LTDebtToWC <= MAX_LONG_TERM_DEBT_TO_WORKING_CAPITAL_RATIO and LTDebtToWC >= 0) 
    
    # TEST 3
    def get_earnings_from_income_stmt(self):
        url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.ticker}&apikey=0F4NZKNHX3TGXQ78'
        r = requests.get(url)

        # Check for retrive success
        if r.status_code != 200:
            print(f"Error: receive status code {r.status_code}")
            return False

        data = r.json()
        if 'annualReports' not in data:
            print("No annual reports found. Response:", data)
            return False

        annual_report = data['annualReports']
        return annual_report
    
    # Earnings stability - Positive net income for the past 10 years & using Alpha Vantage
    def check_earnings_stability(self):
        annual_report = self.get_earnings_from_income_stmt()
        for report in annual_report:
            try:
                if int(report['netIncome']) < 0:
                    return False
            except KeyError:
                print("Error: 'netIncome' or 'fiscalDateEnding' missing key in annual report")
                continue

        return True

    # Get last n years earnings
    def get_last_n_year_earnings(self, n):
        annual_report = self.get_earnings_from_income_stmt()
        earnings = {}
        for i, report in enumerate(annual_report):
            if i >= n:
                return earnings
            fiscal_date = report['fiscalDateEnding']
            year = fiscal_date[:4]
            net_income = int(report['netIncome'])
            earnings[year] = net_income

    # TEST 4
    #Get dividend history for a stock using yahoo finance
    def get_dividend_history(self):
        dividends = self.stock.dividends
        timestamp = dividends.index
        dividends = dividends.values

        current_year = datetime.now().year

        dividend_record = {}
        for i in range(len(timestamp)):
            year = timestamp[i].strftime('%Y')
            if year == str(current_year):
                break
            dividend_record[year] = dividends[i]

        return dividend_record

    # Print dividend history from the current year
    def print_dividend_history(self):
        dividend_record = self.get_dividend_history()
        sorted_history = dict(sorted(dividend_record.items(), reverse=True))
        for year, dividend in sorted_history.items():
            print(f"Dividends paid for {year}: ${dividend:.6f}")

    # Get the dividend record for that stock
    def count_consecutive_years_of_dividend_increase(self):
        dividend_record = self.get_dividend_history()

        consecutive_years = 0
        previous_dividend = None

        for year, dividend in dividend_record.items():
            if previous_dividend is not None:
                if dividend > previous_dividend:
                    consecutive_years += 1
                elif dividend < previous_dividend:
                    consecutive_years = 0
            previous_dividend = dividend

        return consecutive_years + 1

    # Check if the stock has increased its dividend for more than 10 years in a row
    def  check_dividend_record(self):
        return self.count_consecutive_years_of_dividend_increase() >= INCREASED_DIVIDEND_RECORD

    # TEST 5
    # Compute Earnings Growth
    def earnings_growth_last_10_years(self):
        last_10_years_earnings = self.get_last_n_year_earnings(11)
        current_year = datetime.now().year

        try:
            last_3_years_earnings = float(
                last_10_years_earnings[str(current_year - 1)] +
                last_10_years_earnings[str(current_year - 2)] +
                last_10_years_earnings[str(current_year - 3)]
            ) / 3

            first_3_years_earnings = float(
                last_10_years_earnings[str(current_year - 10)] +
                last_10_years_earnings[str(current_year - 9)] +
                last_10_years_earnings[str(current_year - 8)]
            ) / 3
        except KeyError as e:
            print(f"Missing earnings data for year: {e.args[0]}")
            return None

        return int((last_3_years_earnings/first_3_years_earnings) * 100)

    # Check if the last 3 years earnings did grow more than 33% vs the earnings from the 8,9,10 year from the past
    def check_earnings_growth(self):
        earnings_growth = self.earnings_growth_last_10_years()
        if earnings_growth < EARNINGS_GROWTH_THRESHOLD:
            return False
        return True

    # TEST 6 - Moderate P/E Ratio <= 15
    def compute_PE_ratio(self):
        income_stmt = self.stock.income_stmt
        data = income_stmt.loc["Net Income"]
        past_3_years_earnings = [value for value in data[0:3]]
        sum = 0
        for earnings in past_3_years_earnings:
            sum += earnings
        no_shares = self.stock.info['sharesOutstanding']
        avg_earnings_per_share = sum / no_shares
        current_price_per_share = self.stock.info['currentPrice']
        return current_price_per_share / avg_earnings_per_share

    def check_PE_ratio(self):
        return self.compute_PE_ratio() <= PE_RATIO_THRESHOLD

    # TEST 7 - Moderate Price-to-book-ratio
    # 7.1 < 1.5
    def compute_price_to_book_ratio(self):
        # Tangible book value describes the standard definition of book value because it exclude the intangible assets like franchises, brand name, patents and trademarks
        balance_sheet = self.stock.balance_sheet
        tangible_book_value = balance_sheet.loc['Tangible Book Value'].iloc[0]
        no_shares = self.stock.info['sharesOutstanding']
        tangible_book_value_per_share = tangible_book_value / no_shares
        current_price_per_share = self.stock.info['currentPrice']
        return (current_price_per_share / tangible_book_value_per_share)
    
    def check_price_to_book_ratio(self):
        return self.compute_price_to_book_ratio < PRICE_TO_BOOK_RATIO

    # Graham's suggestion is to multiply the P/E ratio by the price-to-book ratio (which includes intangible assets) and see whether the resulting number is below 22.5
    # 7.2 < 22.5
    def compute_price_to_book_ratio_graham(self):
        price_to_book_ratio = self.stock.info['priceToBook']
        pe_ratio = self.compute_PE_ratio()
        return (pe_ratio * price_to_book_ratio)
    
    def check_price_to_book_ratio_graham(self):
        return self.compute_price_to_book_ratio_graham() < PRICE_TO_BOOK_RATIO_GRAHAM

    # print stock indicators value
    def print_results(self):
        print(f"Stock: {self.ticker}")
        print(f"Price: {self.stock.info['currentPrice']}")
        print(f"52-week low: {self.stock.info['fiftyTwoWeekLow']}")
        print(f"52-week high: {self.stock.info['fiftyTwoWeekHigh']}")
        print(f"Sector: {self.stock.info['sector']}")
        marketcap = convert_to_billion(self.stock.info['marketCap'])
        print(f"Market Cap: {marketcap:.2f} billions")
        print(f"Current Ratio: {self.stock.info["currentRatio"]:.2f}")
        print(f"LTDebtToWC: {self.calculate_LTDebt_to_WC():.2f}")
        print(f"Dividend Record is: {self.count_consecutive_years_of_dividend_increase()} consecutive years")
        print(f"P/E Ratio: {self.compute_PE_ratio():.2f}")
        print(f"Price-to-book ratio: {self.compute_price_to_book_ratio():.5f}")
        print(f"Graham's price-to-book ratio: {self.compute_price_to_book_ratio_graham():.5f}")
        # print(f"Earnings Stability over the past 10 years: {self.check_earnings_stability()}")
        # print(f"Earnings Growth over the past 10 years: {self.earnings_growth_last_10_years()}%")
        print('---------------------------------------------------------')