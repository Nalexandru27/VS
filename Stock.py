from datetime import datetime
import requests
import yfinance as yf
from Tresholds import *
import pandas as pd
import os

def convert_to_billion(value):
    return int(value) / BILLION_DIVISION

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.yf = yf.Ticker(ticker)

    # TEST 1
    # Market Capitalization > 2 billion & using yahoo finance
    def get_market_cap(self):
        return self.yf.info['marketCap']

    def check_market_cap(self):
        return float(self.yf.info['marketCap']) >= MIN_MARKET_CAP
    
    # TEST 2.1
    # Current Ratio >= 2 & using yahoo finance
    def get_current_ratio(self):
        return self.yf.info['currentRatio']

    def check_current_ratio(self):
        return float(self.yf.info['currentRatio']) >= MIN_CURRENT_RATIO
    
    # TEST 2.2
    # Long-Term Debt to Working Capital Ratio <= 1 & using yahoo finance
    def calculate_LTDebt_to_WC(self):
        balance_sheet = self.yf.balance_sheet
        current_assets = balance_sheet.loc["Current Assets"].iloc[0]
        current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0]
        working_capital = current_assets - current_liabilities
        long_term_debt = balance_sheet.loc["Long Term Debt"].iloc[0]
        return float(long_term_debt / working_capital)
    
    def check_LTDebt_To_WC(self):
        LTDebtToWC = self.calculate_LTDebt_to_WC()
        return (LTDebtToWC <= MAX_LONG_TERM_DEBT_TO_WORKING_CAPITAL_RATIO and LTDebtToWC >= 0) 
    
    # TEST 3
    def get_income_stmt_from_alphavantage(self):
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
        annual_report = self.get_income_stmt_from_alphavantage()
        i = 0
        for report in annual_report:
            try:
                if i >= 10:
                    break
                if float(report['netIncome']) < 0:
                    return False
                i += 1
            except KeyError:
                print("Error: 'netIncome' or 'fiscalDateEnding' missing key in annual report")
                continue

        return True

    # Get last n years earnings
    def get_last_n_year_earnings(self, n):
        annual_report = self.get_income_stmt_from_alphavantage()
        earnings = {}
        for i, report in enumerate(annual_report):
            if i >= n:
                return earnings
            fiscal_date = report['fiscalDateEnding']
            year = fiscal_date[:4]
            net_income = float(report['netIncome'])
            earnings[year] = net_income

    # TEST 4
    #Get dividend history for a stock using yahoo finance
    def get_dividend_history(self):
        dividends = self.yf.dividends
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
    
    # Read dividend record from excel file
    def get_dividend_record_from_excel(self):
        if os.path.exists(FILE_PATH):
            df = pd.read_excel(FILE_PATH)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'No Years']
        
    # GET DGR 1Y from excel file
    def get_DGR_1Y_from_excel(self):
        if os.path.exists(FILE_PATH):
            df = pd.read_excel(FILE_PATH)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 1Y']
        
    
    # Get DGR 10Y from excel file
    def get_DGR_10Y_from_excel(self):
        if os.path.exists(FILE_PATH):
            df = pd.read_excel(FILE_PATH)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 10Y']

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

        return float((last_3_years_earnings/first_3_years_earnings) * 100)

    # Check if the last 3 years earnings did grow more than 33% vs the earnings from the 8,9,10 year from the past
    def check_earnings_growth(self):
        earnings_growth = self.earnings_growth_last_10_years()
        if earnings_growth < EARNINGS_GROWTH_THRESHOLD:
            return False
        return True

    # TEST 6 - Moderate P/E Ratio <= 15
    def compute_PE_ratio(self):
        income_stmt = self.yf.income_stmt
        data = income_stmt.loc["Net Income"]
        past_3_years_earnings = [value for value in data[0:3]]
        sum = 0
        for earnings in past_3_years_earnings:
            sum += earnings
        no_shares = self.yf.info['sharesOutstanding']
        avg_earnings_per_share = sum / no_shares
        current_price_per_share = self.yf.info['currentPrice']
        return float(current_price_per_share / avg_earnings_per_share)

    def check_PE_ratio(self):
        pe_ratio = self.compute_PE_ratio()
        return pe_ratio <= PE_RATIO_THRESHOLD

    # TEST 7 - Moderate Price-to-book-ratio
    # 7.1 < 1.5
    def compute_price_to_book_ratio(self):
        # Tangible book value describes the standard definition of book value because it exclude the intangible assets like franchises, brand name, patents and trademarks
        balance_sheet = self.yf.balance_sheet
        tangible_book_value = balance_sheet.loc['Tangible Book Value'].iloc[0]
        no_shares = self.yf.info['sharesOutstanding']
        tangible_book_value_per_share = tangible_book_value / no_shares
        current_price_per_share = self.yf.info['currentPrice']
        return float(current_price_per_share / tangible_book_value_per_share)
    
    def check_price_to_book_ratio(self):
        price_to_book_ratio = self.compute_price_to_book_ratio()
        return price_to_book_ratio < PRICE_TO_BOOK_RATIO

    # Graham's suggestion is to multiply the P/E ratio by the price-to-book ratio (which includes intangible assets) and see whether the resulting number is below 22.5
    # 7.2 < 22.5
    def compute_price_to_book_ratio_graham(self):
        price_to_book_ratio = self.yf.info['priceToBook']
        pe_ratio = self.compute_PE_ratio()
        return float(pe_ratio * price_to_book_ratio)
    
    def check_price_to_book_ratio_graham(self):
        price_to_book_ratio_graham = self.compute_price_to_book_ratio_graham()
        return price_to_book_ratio_graham < PRICE_TO_BOOK_RATIO_GRAHAM


    # Get Dividend Yield
    def get_dividend_yield(self):
        return self.yf.info['dividendYield']
    
    # Get cash flows from the past 10 years
    # def get_cash_flows_from_alphavintage(self):
    #     url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={self.ticker}&apikey=0F4NZKNHX3TGXQ78'
    #     r = requests.get(url)

    #     # Check for retrive success
    #     if r.status_code != 200:
    #         print(f"Error: receive status code {r.status_code}")
    #         return False

    #     data = r.json()
    #     if 'annualReports' not in data:
    #         print("No annual reports found. Response:", data)
    #         return False

    #     annual_report = data['annualReports']
    #     return annual_report
    
    # Get last n years of cash flows
    # def get_last_n_years_cash_flows(self, n):
    #     cash_flows = self.get_cash_flows_from_alphavintage()
    #     cash_flows_dict = {}
    #     for i, report in enumerate(cash_flows):
    #         if i >= n:
    #             return cash_flows_dict
    #         fiscal_date = report['fiscalDateEnding']
    #         year = fiscal_date[:4]
    #         operating_cash_flows = float(report['operatingCashflow'])
    #         cash_flows_dict[year] = operating_cash_flows


    # ROCE (return on capital employed) = EBIT / (Total Assets - Current Liabilities)
    # Good indicator to evaluate the managerial economic performance
    def compute_ROCE(self):
        ebit = float(self.yf.financials.loc['EBIT'].iloc[0])
        total_assets = float(self.yf.balance_sheet.loc['Total Assets'].iloc[0])
        current_liabilities = float(self.yf.balance_sheet.loc['Current Liabilities'].iloc[0])
        return float(ebit / (total_assets - current_liabilities))
    
    # # Get last n years of eps
    # def get_last_n_years_eps(self, n):
    #     income_stmt = self.get_income_stmt_from_alphavantage()
    #     eps = {}
    #     for i, report in enumerate(income_stmt):
    #         if i >= n:
    #             return eps
    #         fiscal_date = report['fiscalDateEnding']
    #         year = fiscal_date[:4]
    #         eps = float(report['eps'])
    #         eps[year] = eps


    # print stock indicators value
    # def print_results(self):
    #     print(f"Stock: {self.ticker}")
    #     print(f"Price: {self.yf.info['currentPrice']}")
    #     print(f"52-week low: {self.yf.info['fiftyTwoWeekLow']}")
    #     print(f"52-week high: {self.yf.info['fiftyTwoWeekHigh']}")
    #     print(f"Sector: {self.yf.info['sector']}")
    #     marketcap = convert_to_billion(self.yf.info['marketCap'])
    #     print(f"Market Cap: {marketcap:.2f} billions")
    #     print(f"Current Ratio: {self.yf.info["currentRatio"]:.2f}")
    #     print(f"LTDebtToWC: {self.calculate_LTDebt_to_WC():.2f}")
    #     print(f"Dividend Record is: {self.get_dividend_record_from_excel(FILE_PATH)} consecutive years")
    #     # print(f"Dividend Record is: {self.count_consecutive_years_of_dividend_increase()} consecutive years")
    #     print(f"P/E Ratio: {self.compute_PE_ratio():.2f}")
    #     print(f"Price-to-book ratio: {self.compute_price_to_book_ratio():.5f}")
    #     print(f"Graham's price-to-book ratio: {self.compute_price_to_book_ratio_graham():.5f}")
    #     print(f"Earnings Stability over the past 10 years: {self.check_earnings_stability()}")
    #     print(f"Earnings Growth over the past 10 years: {self.earnings_growth_last_10_years()}%")
    #     print('---------------------------------------------------------')