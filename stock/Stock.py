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

    # Get stock sector
    def get_sector(self):
        db_name = 'companies.db'
        db_crud = db.DatabaseCRUD(db_name)
        company_sector = db_crud.select_company_sector(self.ticker)
        return company_sector

    # Get cash flow statement
    def get_cashflow_data(self):
        try:
            url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={self.ticker}&apikey=WYGPKB8T21WMM6LO'
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
                        'operatingCashFlow': report['operatingCashflow'],
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
            url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.ticker}&apikey=WYGPKB8T21WMM6LO'
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
            url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={self.ticker}&apikey=WYGPKB8T21WMM6LO'
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

            # Get raw values first
            current_assets = db_crud.select_financial_data(financial_statement_id, 'totalCurrentAssets')
            current_liabilities = db_crud.select_financial_data(financial_statement_id, 'totalCurrentLiabilities')

            # Check for None or 'None' string values
            if (current_assets is None or current_assets == 'None' or 
                current_liabilities is None or current_liabilities == 'None'):
                return 0

            # Convert to integers after checking
            try:
                current_assets = int(current_assets)
                current_liabilities = int(current_liabilities)
            except (ValueError, TypeError):
                return 0

            if current_liabilities == 0:
                return 0
                
            return float(current_assets / current_liabilities)
        except Exception as e:
            print(f"Error getting current ratio for {self.ticker}: {e}")
            return 0

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

            # Get the values and handle None cases
            current_assets = db_crud.select_financial_data(financial_statement_id, 'totalCurrentAssets')
            current_liabilities = db_crud.select_financial_data(financial_statement_id, 'totalCurrentLiabilities')
            long_term_debt = db_crud.select_financial_data(financial_statement_id, 'longTermDebt')

            # Check for None or 'None' string values
            if (current_assets is None or current_assets == 'None' or 
                current_liabilities is None or current_liabilities == 'None' or
                long_term_debt is None or long_term_debt == 'None'):
                return 0

            # Convert to integers
            try:
                current_assets = int(current_assets)
                current_liabilities = int(current_liabilities)
                long_term_debt = int(long_term_debt)
            except (ValueError, TypeError):
                return 0

            working_capital = current_assets - current_liabilities
            
            # Avoid division by zero
            if working_capital == 0:
                return 0

            return float(long_term_debt / working_capital)
        except Exception as e:
            print(f"Error calculating LTDebt to WC for {self.ticker}: {e}")
            return 0

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
            db_name = 'companies.db'
            ticker = self.ticker
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(ticker)
            last_year = datetime.now().year - 2
            financial_statement_id = db_crud.select_financial_statement(company_id, 'balance_sheet', last_year)

            # Get all debt components
            short_term_debt = db_crud.select_financial_data(financial_statement_id, 'shortTermDebt')
            long_term_debt = db_crud.select_financial_data(financial_statement_id, 'longTermDebt')
            total_equity = db_crud.select_financial_data(financial_statement_id, 'totalEquity')

            # Check for None or 'None' string values
            if (short_term_debt is None or short_term_debt == 'None' or
                long_term_debt is None or long_term_debt == 'None' or
                total_equity is None or total_equity == 'None'):
                return 0

            # Convert to integers
            try:
                short_term_debt = int(short_term_debt)
                long_term_debt = int(long_term_debt)
                total_equity = int(total_equity)
            except (ValueError, TypeError):
                return 0

            total_debt = short_term_debt + long_term_debt
            total_capital = total_debt + total_equity

            # Avoid division by zero
            if total_capital == 0:
                return 0

            return float(total_debt / total_capital)
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
            if total_assets is None:
                return 0
            current_liabilities = db_crud.select_financial_data(balance_sheet_id, 'totalCurrentLiabilities')
            if current_liabilities is None:
                return 0
            else:
                denominator = total_assets - current_liabilities
                if denominator == 0:
                    return 0
                income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
                ebit = db_crud.select_financial_data(income_statement_id, 'ebit')
                if ebit is None:
                    return 0
                return float(ebit / denominator)
        except Exception as e:
            print(f"Error calculating ROCE for {self.ticker}: {e}")
            return 0
    
    # Get return on equity (ROE)
    def return_on_equity(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
            net_income = db_crud.select_financial_data(income_statement_id, 'netIncome')
            
            if net_income is None or net_income == 'None':
                return 0

            balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            total_equity = db_crud.select_financial_data(balance_sheet_id, 'totalEquity')
            
            if total_equity is None or total_equity == 'None' or int(total_equity) == 0:
                return 0

            return float(net_income / total_equity)
        except Exception as e:
            print(f"Error calculating ROE for {self.ticker}: {e}")
            return 0    
    
    # Get operating income margin
    def operating_income_margin(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
            operating_income = db_crud.select_financial_data(income_statement_id, 'operatingIncome')
            if operating_income is None:
                return 0
            revenue = db_crud.select_financial_data(income_statement_id, 'revenue')
            if revenue is None or revenue == 0:
                return 0
            return float(operating_income / revenue)
        except Exception as e:
            print(f"Error calculating operating income margin for {self.ticker}: {e}")
            return 0

    # Get shares outstanding trend - increase / decrease / consistent decrease
    def ordinary_shares_number_trend_analysis(self):
        db_name = 'companies.db'
        db_crud = db.DatabaseCRUD(db_name)
        company_id = db_crud.select_company(self.ticker)
        current_year = datetime.now().year
        list = []
        balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
        while(balance_sheet_id is not None):
            sharesOutsatnding = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if sharesOutsatnding is not None:
                list.append(sharesOutsatnding)
            current_year -= 1
            balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)

        if len(list) > 2:
            cnt = 0
            for i in range(len(list)-1):
                if list[i] > list[i+1]:
                    return "increase"
                elif list[i] < list[i+1]:
                    cnt += 1
            if cnt == len(list)-1:
                return "consistent decrease"
            else:
                return "chaotic or 0 decrease"
            
    #  Get EPS
    def get_EPS(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
            net_income = db_crud.select_financial_data(income_statement_id, 'netIncome')
            if net_income is None:
                return 0
            balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            no_shares = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if no_shares is None or no_shares == 0:
                return 0
            return float(net_income / no_shares)
        except Exception as e:
            print(f"Error calculating EPS for {self.ticker}: {e}")
            return 0
    
    # Get Earnings Payout Ratio
    def earnings_payout_ratio(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            last_year = current_year - 2

            # Get cashflow statement data
            cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', last_year)
            dividend_payout = abs(db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout'))
            
            # Get income statement data
            income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', last_year)
            net_income = db_crud.select_financial_data(income_statement_id, 'netIncome')

            if dividend_payout is None or net_income is None or float(net_income) == 0:
                return 0
                
            return float(dividend_payout) / float(net_income)
        except Exception as e:
            print(f"Error calculating earnings payout ratio for {self.ticker}: {e}")
            return 0

    # Get FCF per share
    def get_fcf_per_share(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)

            # Get operating cash flow
            operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')

            # Get capital expenditures
            capital_expenditures = db_crud.select_financial_data(cashflow_statement_id, 'capitalExpenditures')

            # Check for None values
            if operating_cash_flow is None or capital_expenditures is None:
                return 0
                
            # Convert to integers
            try:
                operating_cash_flow = int(operating_cash_flow)
                capital_expenditures = int(capital_expenditures)
            except (ValueError, TypeError):
                return 0

            free_cash_flow = operating_cash_flow - capital_expenditures

            # Get shares outstanding
            balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            no_shares = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')

            if no_shares is None or no_shares == 'None':
                return 0
                
            try:
                no_shares = int(no_shares)
            except (ValueError, TypeError):
                return 0

            if no_shares == 0:
                return 0
                
            return float(free_cash_flow / no_shares)
        except Exception as e:
            print(f"Error calculating FCF per share for {self.ticker}: {e}")
            return 0
        
    # Compute FCF Payout Ratio
    def FCF_Payout_Ratio(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)

            # Get operating cash flow
            operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')
                
            capital_expenditures = db_crud.select_financial_data(cashflow_statement_id, 'capitalExpenditures')

            if operating_cash_flow is None or capital_expenditures is None:
                return 0
                
            # Convert to integers
            try:
                operating_cash_flow = int(operating_cash_flow)
                capital_expenditures = int(capital_expenditures)
            except (ValueError, TypeError):
                return 0

            free_cash_flow = operating_cash_flow - capital_expenditures

            # Get dividend payout
            dividendPayout = db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout')
            if dividendPayout is None or dividendPayout == 'None':
                return 0
                
            try:
                dividendPayout = abs(int(dividendPayout))
            except (ValueError, TypeError):
                return 0

            if free_cash_flow == 0:
                return 0
                
            return float(dividendPayout / free_cash_flow)
        except Exception as e:
            print(f"Error calculating FCF Payout Ratio for {self.ticker}: {e}")
            return 0
        
    # Compute Operating Cash Flow per Share
    def get_operating_cash_flow_per_share(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)
            
            operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')

            if operating_cash_flow is None:
                return 0
            
            balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)

            no_shares = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if no_shares is None or no_shares == 0:
                return 0
            
            return float(operating_cash_flow / no_shares)
        except Exception as e:
            print(f"Error calculating operating cash flow per share for {self.ticker}: {e}")
            return 0
        
    # Compute Operating Cash Flow Payout Ratio
    def get_operating_cash_flow_payout_ratio(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)
            
            operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')
            
            if operating_cash_flow is None or operating_cash_flow == 0:
                return 0
            
            dividendPayout = abs(db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout'))
            if dividendPayout is None:
                return 0
            
            return dividendPayout / operating_cash_flow
        except Exception as e:
            print(f"Error calculating operating cash flow payout ratio for {self.ticker}: {e}")
            return 0
        
    def dividends_per_share(self):
        try:
            db_name = 'companies.db'
            db_crud = db.DatabaseCRUD(db_name)
            company_id = db_crud.select_company(self.ticker)
            current_year = datetime.now().year
            cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)
            dividendPayout = abs(db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout'))
            if dividendPayout is None:
                return 0
            balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            no_shares = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if no_shares is None or no_shares == 0:
                return 0
            return float(dividendPayout / no_shares)
        except Exception as e:
            print(f"Error calculating dividends per share for {self.ticker}: {e}")
            return 0

    # print stock indicators value
    # def print_results(self):
    #     print(f"Stock: {self.ticker}")
    #     print(f"Sector: {self.yf.info['sector']}")
    #     print(f"Price: {self.yf.info['currentPrice']}")
    #     print(f"52-week low: {self.yf.info['fiftyTwoWeekLow']}")
    #     print(f"52-week high: {self.yf.info['fiftyTwoWeekHigh']}")
    #     marketcap = convert_to_billion(self.yf.info['marketCap'])
    #     print(f"Market Cap: {marketcap:.2f} billions")
    #     print(f"Current Ratio: {self.yf.info["currentRatio"]:.2f}")
    #     print(f"LTDebtToWC: {self.calculate_LTDebt_to_WC():.2f}")
    #     print(f"Dividend Record is: {self.get_dividend_record_from_excel(FILE_PATH_1)} consecutive years")
    #     print(f"Dividend Yield: {self.get_dividend_yield():.2f}")
    #     print(f"Earnings Payout Ratio: {self.yf.info['payoutRatio']:.2f}%")
    #     print(f"FCF Payout Ratio: {self.FCF_Payout_Ratio() * 100:.2f}%")
    #     print(f"Debt to Total Capital Ratio: {self.Debt_to_Total_Capital_Ratio() * 100:.2f}")
    #     print(f"Return on Equity: {self.return_on_equity():.2f}%")
    #     print(f"ROCE: {self.compute_ROCE():.2f}")
    #     print(f"P/E Ratio: {self.compute_PE_ratio():.2f}")
    #     print(f"Price-to-book ratio: {self.compute_price_to_book_ratio():.2f}")
    #     print(f"Graham's price-to-book ratio: {self.compute_price_to_book_ratio_graham():.2f}")
    #     print(f"Earnings Stability over the past 10 years: {self.earnings_stability()}")
    #     print(f"Earnings Growth over the past 10 years: {self.earnings_growth_last_10_years():.2f}%")
    #     print('---------------------------------------------------------')