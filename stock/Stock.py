from datetime import datetime
import requests
import yfinance as yf
from utils.Tresholds import *
import pandas as pd
import os
import database.DatabaseCRUD as db

def convert_to_billion(value):
    return int(value) / BILLION_DIVISION

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.yf = yf.Ticker(ticker)

    # Get cash flow statement
    def get_cashflow_data(self):
        try:
            url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={self.ticker}&apikey=43KL4PW74AWGDJZI'
            r = requests.get(url)
            data = r.json()
            annual_reports = data['annualReports']
            number_of_years = len(annual_reports)
            i = 0
            cashflow_data = {}
            for report in annual_reports:
                if i < number_of_years:
                    date = report['fiscalDateEnding'].split('-')[0]
                    cashflow_data[date] = {
                        'operatingCashFow': report['operatingCashflow'],
                        'capitalExpenditures': report['capitalExpenditures'],
                        'cashFlowInvesting': report['cashflowFromInvestment'],
                        'cashFlowFinancing': report['cashflowFromFinancing'],
                        'dividendPayout': report['dividendPayout'],
                        'dividendPayoutPreferredStock': report['dividendPayoutPreferredStock'],
                        'changeInOperatingAssets': report['changeInOperatingAssets'],
                        'changeInOperatingLiabilities': report['changeInOperatingLiabilities']
                    }
                    i += 1
                else:
                    break
            df = pd.DataFrame.from_dict(cashflow_data, orient='index')
            df.index.name = 'fiscal_date_ending'
            return df
        except Exception as e:
            print(f"Error getting cashflow statement for {self.ticker}: {e}")
            return None
    
    # Get income statement
    def get_income_statement(self):
        try:
            url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.ticker}&apikey=43KL4PW74AWGDJZI'
            r = requests.get(url)
            data = r.json()
            annual_reports = data['annualReports']
            number_of_years = len(annual_reports)
            i = 0
            income_statement = {}
            for report in annual_reports:
                if i < number_of_years:
                    date = report['fiscalDateEnding'].split('-')[0]
                    income_statement[date] = {
                        'grossProfit': report['grossProfit'],
                        'revenue': report['totalRevenue'],
                        'COGS': report['costofGoodsAndServicesSold'],
                        'operatingIncome': report['operatingIncome'],
                        'SG&A': report['sellingGeneralAndAdministrative'],
                        'researchAndDevelopment': report['researchAndDevelopment'],
                        'depreciationAndAmortization': report['depreciationAndAmortization'],
                        'incomeBeforeTax': report['incomeBeforeTax'],
                        'netIncomeFromContinuingOps': report['netIncomeFromContinuingOperations'],
                        'ebit': report['ebit'],
                        'netIncome': report['netIncome'],
                        'interestExpense': report['interestExpense']
                    }
                    i += 1
                else:
                    break
            df = pd.DataFrame.from_dict(income_statement, orient='index')
            df.index.name = 'fiscal_date_ending'
            return df
        except Exception as e:
            print(f"Error getting income statement for {self.ticker}: {e}")
            return None
        
    # Compute AFFO
    # Base FFO = Net Income + Depreciation & Amortization
    # + Interest Expense
    # + Change in Operating Liabilities
    # + Change in Operating Assets
    # + Depreciation Depletion And Amortization (additional)
    # Extended FFO
    # - Capital Expenditures
    # + Operating Cash Flow Adjustments
    # - Dividend Payout


    # Get balance sheet
    def get_balance_sheet(self):
        try:
            url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={self.ticker}&apikey=H03ZN6G32VUTNCGT'
            r = requests.get(url)
            data = r.json()
            annual_reports = data['annualReports']
            number_of_years = len(annual_reports)
            i = 0
            balance_sheet = {}
            for report in annual_reports:
                if i < number_of_years:
                    date = report['fiscalDateEnding'].split('-')[0]
                    balance_sheet[date] = {
                        'totalAssets': report['totalAssets'],
                        'totalCurrentAssets': report['totalCurrentAssets'],
                        'cashAndCashEquivalentsAtCarryingValue': report['cashAndCashEquivalentsAtCarryingValue'],
                        'cashAndShortTermInvestments': report['cashAndShortTermInvestments'],
                        'inventory': report['inventory'],
                        'currentNetReceivables': report['currentNetReceivables'],
                        'propertyPlantEquipment': report['propertyPlantEquipment'],
                        'intagibleAssets': report['intangibleAssets'],
                        'goodwill': report['goodwill'],
                        'longTermInvestments': report['longTermInvestments'],
                        'shortTermInvestments': report['shortTermInvestments'],
                        'otherCurrentAssets': report['otherCurrentAssets'],
                        'otherNonCurrentAssets': report['otherNonCurrentAssets'],
                        'totalLiabilities': report['totalLiabilities'],
                        'totalCurrentLiabilities': report['totalCurrentLiabilities'],
                        'currentAccountsPayable': report['currentAccountsPayable'],
                        'deferredRevenue': report['deferredRevenue'],
                        'currentDebt': report['currentDebt'],
                        'shortTermDebt': report['shortTermDebt'],
                        'capitalLeaseObligations': report['capitalLeaseObligations'],
                        'longTermDebt': report['longTermDebt'],
                        'otherCurrentLiabilities': report['otherCurrentLiabilities'],
                        'otherNonCurrentLiabilities': report['otherNonCurrentLiabilities'],
                        'totalEquity': report['totalShareholderEquity'],
                        'treasuryStock': report['treasuryStock'],
                        'retainedEarnings': report['retainedEarnings'],
                        'commonStock': report['commonStock'],
                        'sharesOutstanding': report['commonStockSharesOutstanding']
                    }
                    i += 1
                else:
                    break
            df = pd.DataFrame.from_dict(balance_sheet, orient='index')
            df.index.name = 'fiscal_date_ending'
            return df
        except Exception as e:
            print(f"Error getting balance sheet for {self.ticker}: {e}")
            return None

    # TEST 1
    # Get market cap from yahoo finance
    def get_market_cap(self):
        try:
            return self.yf.info['marketCap']
        except Exception as e:
            print(f"Error getting market cap for {self.ticker}: {e}")
            return 0
    
    # TEST 2
    # Get current ratio from database
    def get_current_ratio(self):
        try:
            db_name = 'companies.db'
            ticker = self.ticker
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(ticker)
            last_year = datetime.now().year - 2
            financial_statement_id = db_crud.select_financial_statement(company_id, 'balance_sheet', last_year)
            current_assets = db_crud.select_financial_data(financial_statement_id, 'current_assets')
            current_liabilities = db_crud.select_financial_data(financial_statement_id, 'current_liabilities')
            return int(current_assets / current_liabilities)
        except Exception as e:
            print(f"Error getting current ratio for {self.ticker}: {e}")
            return 0
        # try:
        #     if self.yf.info.get('sector') == 'Financial Services':
        #         try:
        #             balance_sheet = self.yf.balance_sheet
                    
        #             # Safely access keys with fallback to 0 if not present
        #             cash_and_cash_equivalents = (
        #                 balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
        #                 if 'Cash And Cash Equivalents' in balance_sheet.index else 0
        #             )
        #             receivables = (
        #                 balance_sheet.loc['Receivables'].iloc[0]
        #                 if 'Receivables' in balance_sheet.index else 0
        #             )
        #             other_short_term_investments = (
        #                 balance_sheet.loc['Other Short Term Investments'].iloc[0]
        #                 if 'Other Short Term Investments' in balance_sheet.index else 0
        #             )
                    
        #             current_assets = cash_and_cash_equivalents + receivables + other_short_term_investments
                    
        #             if current_assets != 0:
        #                 total_liabilities_net_minority_interest = (
        #                     balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0]
        #                     if 'Total Liabilities Net Minority Interest' in balance_sheet.index else 1
        #                 )  # Default to 1 to avoid division by zero

        #                 long_term_debt_and_capital_lease_obligations = (
        #                     balance_sheet.loc['Long Term Debt And Capital Lease Obligations'].iloc[0]
        #                     if 'Long Term Debt And Capital Lease Obligations' in balance_sheet.index else 0
        #                 )

        #                 if total_liabilities_net_minority_interest != 0 and long_term_debt_and_capital_lease_obligations != 0:
        #                     current_liabilities = total_liabilities_net_minority_interest - long_term_debt_and_capital_lease_obligations
        #                     return float(current_assets / current_liabilities)
        #                 else:
        #                     current_liabilities = (
        #                         balance_sheet.loc['Payables And Accrued Expenses'].iloc[0]
        #                         if 'Payables And Accrued Expenses' in balance_sheet.index else 1
        #                     )  # Default to 1 to avoid division by zero
        #                     if current_liabilities != 1:
        #                         return float(current_assets / current_liabilities)
        #         except Exception as e:
        #             print(f"Error calculating current ratio from balance sheet for {self.ticker}: {e}")
                
        #     if self.yf.info['currentRatio'] is not None:
        #         return float(self.yf.info['currentRatio'])
            
        # except Exception as e:
        #     print(f"Error getting current ratio for {self.ticker}: {e}")
            
        # return 0

    # TEST 3
    # Get long term debt to working capital ratio from database
    def get_LTDebt_to_WC(self):
        try:
            db_name = 'companies.db'
            ticker = self.ticker
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(ticker)
            last_year = datetime.now().year - 2
            financial_statement_id = db_crud.select_financial_statement(company_id, 'balance_sheet', last_year)
            current_assets = db_crud.select_financial_data(financial_statement_id, 'totalCurrentAssets')
            current_liabilities = db_crud.select_financial_data(financial_statement_id, 'totalCurrentLiabilities')
            working_capital = current_assets - current_liabilities
            long_term_debt = db_crud.select_financial_data(financial_statement_id, 'longTermDebt')
            return int(long_term_debt / working_capital)
        except Exception as e:
            print(f"Error calculating LTDebt to WC for {self.ticker}: {e}")
            return 0
        # try:
        #     balance_sheet = self.yf.balance_sheet
        #     # Check if 'Long Term Debt' exists in the index
        #     long_term_debt = balance_sheet.loc['Long Term Debt'].iloc[0] if 'Long Term Debt' in balance_sheet.index else 0

        #     if self.yf.info.get('sector') == 'Financial Services':
        #         try:
        #             # Check for the existence of keys before accessing them
        #             cash_and_cash_equivalents = (
        #                 balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
        #                 if 'Cash And Cash Equivalents' in balance_sheet.index else 0
        #             )
        #             receivables = (
        #                 balance_sheet.loc['Receivables'].iloc[0]
        #                 if 'Receivables' in balance_sheet.index else 0
        #             )
        #             other_short_term_investments = (
        #                 balance_sheet.loc['Other Short Term Investments'].iloc[0]
        #                 if 'Other Short Term Investments' in balance_sheet.index else 0
        #             )
                    
        #             current_assets = cash_and_cash_equivalents + receivables + other_short_term_investments
        #             current_liabilities = (
        #                 balance_sheet.loc['Payables And Accrued Expenses'].iloc[0]
        #                 if 'Payables And Accrued Expenses' in balance_sheet.index else 1
        #             )  # Default to 1 to avoid division by zero
                    
        #             working_capital = current_assets - current_liabilities
        #             if working_capital > 0:
        #                 return float(long_term_debt / working_capital)
        #         except Exception as e:
        #             print(f"Error calculating working capital for financial services sector for {self.ticker}: {e}")
            
        #     # For non-financial services or fallback logic
        #     try:
        #         working_capital = balance_sheet.loc["Working Capital"].iloc[0] if "Working Capital" in self.yf.balance_sheet.index else 0
        #         if working_capital == 0:
        #             current_assets = (
        #                 balance_sheet.loc['Current Assets'].iloc[0]
        #                 if 'Current Assets' in balance_sheet.index else 0
        #             )
        #             current_liabilities = (
        #                 balance_sheet.loc['Current Liabilities'].iloc[0]
        #                 if 'Current Liabilities' in balance_sheet.index else 1
        #             )  # Default to 1 to avoid division by zero
                    
        #             working_capital = current_assets - current_liabilities
        #             if working_capital > 0:
        #                 return float(long_term_debt / working_capital)
        #         else:
        #             return float(long_term_debt / working_capital)
        #     except Exception as e:
        #         print(f"Error calculating working capital for non-financial services sector for {self.ticker}: {e}")
            
        # except Exception as e:
        #     print(f"Error calculating LTDebt to WC for {self.ticker}: {e}")

        # # Final fallback if all else fails
        # return 0

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
        
    # GET DGR 3Y from excel file
    def get_DGR_3Y_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 3Y']
        
    # GET DGR 5Y from excel file
    def get_DGR_5Y_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 5Y']
    
    # Get DGR 10Y from excel file
    def get_DGR_10Y_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 10Y']

    # TEST 5
    # Compute Earnings Growth
    def earnings_growth_last_10_years(self):
        db_name = 'companies.db'
        ticker = self.ticker
        db_crud = db.DatabaseCRUD(db_name)
        company_id = db_crud.select_company(ticker)
        current_year = datetime.now().year - 1
        last_3_years = []
        for year in range(current_year - 3, current_year):
            financial_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
            net_income = db_crud.select_financial_data(financial_statement_id, 'netIncome')
            last_3_years.append(net_income)
        last_3_years_series = pd.Series(last_3_years)
        first_3_years = []
        for year in range(current_year - 10, current_year - 7):
            financial_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
            net_income = db_crud.select_financial_data(financial_statement_id, 'netIncome')
            first_3_years.append(net_income)
        first_3_years_series = pd.Series(first_3_years)
        try:
            return float((last_3_years_series.mean() / first_3_years_series.mean()) * 100)
        except KeyError as e:
            print(f"Missing earnings data for year: {e.args[0]}")
            return None

    # TEST 6
    # Check earnings stability over the past 10 years
    def earnings_stability(self):
        db_name = 'companies.db'
        ticker = self.ticker
        db_crud = db.DatabaseCRUD(db_name)
        company_id = db_crud.select_company(ticker)
        last_year = datetime.now().year - 2
        for year in range(last_year - 10, last_year):
            financial_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
            net_income = db_crud.select_financial_data(financial_statement_id, 'netIncome')
            if net_income < 0:
                return False
        return True

    # Get P/E Ratio using the average earnings per share over the past 3 years
    def compute_PE_ratio(self):
        try:
            db_crud = db.DatabaseCRUD('companies.db')
            company_id = db_crud.select_company(self.ticker)
            past_3_years_earnings = []
            for year in range(datetime.now().year - 5, datetime.now().year - 2):
                financial_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
                net_income = db_crud.select_financial_data(financial_statement_id, 'netIncome')
                past_3_years_earnings.append(net_income)
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
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            total_assets = db_crud.select_financial_data(balance_sheet_id, 'totalAssets')
            current_liabilities = db_crud.select_financial_data(balance_sheet_id, 'totalCurrentLiabilities')
            income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
            ebit = db_crud.select_financial_data(income_statement_id, 'ebit')
            # total_assets = float(self.yf.balance_sheet.loc['Total Assets'].iloc[0])
            # ebit = float(self.yf.financials.loc['EBIT'].iloc[0])
            # current_liabilities = float(self.yf.balance_sheet.loc['Current Liabilities'].iloc[0])
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
            
    def get_fcf_per_share(self):
        try:
            free_cash_flow = self.yf.cashflow.loc['Free Cash Flow'].iloc[0]
            no_shares = self.yf.info['sharesOutstanding']
            return float(free_cash_flow / no_shares)
        except Exception as e:
            print(f"Error calculating FCF per share for {self.ticker}: {e}")
            return 0
        
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
        
    # Compute Operating Cash Flow per Share
    def get_operating_cash_flow_per_share(self):
        try:
            operating_cash_flow = self.yf.cashflow.loc['Operating Cash Flow'].iloc[0]
            no_shares = self.yf.info['sharesOutstanding']
            return float(operating_cash_flow / no_shares)
        except Exception as e:
            print(f"Error calculating operating cash flow per share for {self.ticker}: {e}")
            return 0
        
    # Compute Operating Cash Flow Payout Ratio
    def get_operating_cash_flow_payout_ratio(self):
        try:
            operating_cash_flow = self.yf.cashflow.loc['Operating Cash Flow'].iloc[0]
            dividens_paid = abs(self.yf.cashflow.loc['Cash Dividends Paid'].iloc[0])
            if operating_cash_flow == 0:
                return 0
            return dividens_paid / operating_cash_flow
        except Exception as e:
            print(f"Error calculating operating cash flow payout ratio for {self.ticker}: {e}")
            return 0
        
    def dividends_per_share(self):
        try:
            dividens_paid = self.yf.cashflow.loc['Cash Dividends Paid'].iloc[0]
            if dividens_paid < 0: # If the value is negative, it means that the company is paying dividends
                dividens_paid = dividens_paid * (-1)
            no_shares = self.yf.info['sharesOutstanding']
            return float(dividens_paid / no_shares)
        except Exception as e:
            print(f"Error calculating dividends per share for {self.ticker}: {e}")
            return 0

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
        print(f"Earnings Stability over the past 10 years: {self.earnings_stability()}")
        print(f"Earnings Growth over the past 10 years: {self.earnings_growth_last_10_years():.2f}%")
        print('---------------------------------------------------------')