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

    # Get market cap from yahoo finance
    def get_market_cap(self):
        try:
            return self.yf.info['marketCap']
        except Exception as e:
            print(f"Error getting market cap for {self.ticker}: {e}")
            return 0
    
    # Get current ratio from yahoo finance
    def get_current_ratio(self):
        try:
            return self.yf.info['currentRatio']
        except Exception as e:
            print(f"Error getting current ratio for {self.ticker}: {e}")
            return 0

    # Get long term debt to working capital ratio from yahoo finance
    def calculate_LTDebt_to_WC(self):
        try:
            balance_sheet = self.yf.balance_sheet
            current_assets = balance_sheet.loc["Current Assets"].iloc[0]
            current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0]
            working_capital = current_assets - current_liabilities
            long_term_debt = balance_sheet.loc["Long Term Debt"].iloc[0]
            return float(long_term_debt / working_capital)
        except Exception as e:
            print(f"Error calculating LTDebt to WC for {self.ticker}: {e}")
            return 0
    
     
    # Get income statement from alphavantage
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
    
    # Read dividend record from excel file
    def get_dividend_record_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'No Years']
        
    # GET DGR 1Y from excel file
    def get_DGR_1Y_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 1Y']
        
    
    # Get DGR 10Y from excel file
    def get_DGR_10Y_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
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

    # Get P/E Ratio using the average earnings per share over the past 3 years
    def compute_PE_ratio(self):
        try:
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
        except Exception as e:
            print(f"Error calculating PE ratio for {self.ticker}: {e}")
            return 0

    # TEST 7 - Moderate Price-to-book-ratio
    # 7.1 < 1.5
    def compute_price_to_book_ratio(self):
        # Tangible book value describes the standard definition of book value because it exclude the intangible assets like franchises, brand name, patents and trademarks
        try:
            balance_sheet = self.yf.balance_sheet
            tangible_book_value = balance_sheet.loc['Tangible Book Value'].iloc[0]
            no_shares = self.yf.info['sharesOutstanding']
            tangible_book_value_per_share = tangible_book_value / no_shares
            current_price_per_share = self.yf.info['currentPrice']
            return float(current_price_per_share / tangible_book_value_per_share)
        except Exception as e:
            print(f"Error calculating price to book ratio for {self.ticker}: {e}")
            return 0

    # Graham's suggestion is to multiply the P/E ratio by the price-to-book ratio (which includes intangible assets) and see whether the resulting number is below 22.5
    # 7.2 < 22.5
    def compute_price_to_book_ratio_graham(self):
        try:
            price_to_book_ratio = self.yf.info['priceToBook']
            pe_ratio = self.compute_PE_ratio()
            return float(pe_ratio * price_to_book_ratio)
        except Exception as e:
            print(f"Error calculating price to book ratio for {self.ticker}: {e}")
            return 0

    # Get Dividend Yield
    def get_dividend_yield(self):
        return self.yf.info['dividendYield']
    
    # Compute FCF Payout Ratio
    def FCF_Payout_Ratio(self):
        try:
            free_cash_flow = self.yf.cashflow.loc['Free Cash Flow'].iloc[0]
            dividens_paid = abs(self.yf.cashflow.loc['Cash Dividends Paid'].iloc[0])
            if free_cash_flow == 0:
                return 0
            return dividens_paid / free_cash_flow
        except Exception as e:
            print(f"Error calculating FCF Payout Ratio for {self.ticker}: {e}")
            return 0  # Ensure a return value even in case of failure
    
    # Compute Debt to Total Capital Ratio
    def Debt_to_Total_Capital_Ratio(self):
        try:
            balance_sheet = self.yf.balance_sheet
            total_debt = float(balance_sheet.loc['Total Debt'].iloc[0])
            stockholders_equity = float(balance_sheet.loc['Stockholders Equity'].iloc[0])
            return float(total_debt / (total_debt + stockholders_equity))
        except Exception as e:
            print(f"Error calculating Debt to Total Capital Ratio for {self.ticker}: {e}")
            return 0
    
    # ROCE (return on capital employed) = EBIT / (Total Assets - Current Liabilities)
    # Good indicator to evaluate the managerial economic performance
    def compute_ROCE(self):
        try:
            ebit = float(self.yf.financials.loc['EBIT'].iloc[0])
            total_assets = float(self.yf.balance_sheet.loc['Total Assets'].iloc[0])
            current_liabilities = float(self.yf.balance_sheet.loc['Current Liabilities'].iloc[0])
            return float(ebit / (total_assets - current_liabilities))
        except Exception as e:
            print(f"Error calculating ROCE for {self.ticker}: {e}")
            return 0
    
    # Get return on equity (ROE)
    def return_on_equity(self):
        try:
            return float(self.yf.info['returnOnEquity'] * 100)
        except Exception as e:
            print(f"Error calculating ROE for {self.ticker}: {e}")
            return 0
    
    # Get operating income margin
    def operating_income_margin(self):
        try:
            return float(self.yf.info['operatingMargins'] * 100)
        except Exception as e:
            print(f"Error calculating operating income margin for {self.ticker}: {e}")
            return 0

    # Get shares outstanding trend - increase / decrease / consistent decrease
    def ordinary_shares_number_trend_analysis(self):
        balance_sheet = self.yf.balance_sheet
        df = balance_sheet.loc["Ordinary Shares Number"].dropna().tolist()

        if len(df) > 2:
            cnt = 0
            for i in range(len(df)-1):
                if df[i] > df[i+1]:
                    return "increase"
                elif df[i] < df[i+1]:
                    cnt += 1
            if cnt == len(df)-1:
                return "consistent decrease"
            else:
                return "chaotic or 0 decrease"
            
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
    def print_results(self):
        print(f"Stock: {self.ticker}")
        print(f"Sector: {self.yf.info['sector']}")
        print(f"Price: {self.yf.info['currentPrice']}")
        print(f"52-week low: {self.yf.info['fiftyTwoWeekLow']}")
        print(f"52-week high: {self.yf.info['fiftyTwoWeekHigh']}")
        marketcap = convert_to_billion(self.yf.info['marketCap'])
        print(f"Market Cap: {marketcap:.2f} billions")
        print(f"Current Ratio: {self.yf.info["currentRatio"]:.2f}")
        print(f"LTDebtToWC: {self.calculate_LTDebt_to_WC():.2f}")
        print(f"Dividend Record is: {self.get_dividend_record_from_excel(FILE_PATH_1)} consecutive years")
        print(f"Dividend Yield: {self.get_dividend_yield():.2f}")
        print(f"Earnings Payout Ratio: {self.yf.info['payoutRatio']:.2f}%")
        print(f"FCF Payout Ratio: {self.FCF_Payout_Ratio() * 100:.2f}%")
        print(f"Debt to Total Capital Ratio: {self.Debt_to_Total_Capital_Ratio() * 100:.2f}")
        print(f"Return on Equity: {self.return_on_equity():.2f}%")
        print(f"ROCE: {self.compute_ROCE():.2f}")
        print(f"P/E Ratio: {self.compute_PE_ratio():.2f}")
        print(f"Price-to-book ratio: {self.compute_price_to_book_ratio():.2f}")
        print(f"Graham's price-to-book ratio: {self.compute_price_to_book_ratio_graham():.2f}")
        print(f"Earnings Stability over the past 10 years: {self.check_earnings_stability()}")
        print(f"Earnings Growth over the past 10 years: {self.earnings_growth_last_10_years():.2f}%")
        print('---------------------------------------------------------')