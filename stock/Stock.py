import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from datetime import datetime
import requests
from utils.Constants import *
import pandas as pd
import os
import database.DatabaseCRUD as db
from utils.SafeDivide import safe_divide

def convert_to_billion(value):
    return int(value) / BILLION_DIVISION

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.db_crud = db.DatabaseCRUD()

    # Get stock sector
    def get_sector(self):
        return self.db_crud.select_company_sector(self.ticker)

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
            url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={self.ticker}&apikey=43KL4PW74AWGDJZI'
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
    # Get market cap
    def get_market_cap(self):
        try:
            latest_price = self.db_crud.get_last_price(self.ticker)
            if latest_price is None:
                return 0
                
            company_id = self.db_crud.select_company(self.ticker)
            if not company_id:
                return 0
                
            balance_sheet_id = self.db_crud.select_financial_statement(
                company_id, 'balance_sheet', datetime.now().year - 2
            )
            if not balance_sheet_id:
                return 0
                
            shares_outstanding = self.db_crud.select_financial_data(
                balance_sheet_id, 'sharesOutstanding'
            )
            
            if shares_outstanding is None or shares_outstanding == 'None':
                return 0
                
            try:
                shares_outstanding = float(shares_outstanding)
            except (ValueError, TypeError):
                return 0
                
            return latest_price * shares_outstanding
        except Exception as e:
            print(f"Error getting market cap for {self.ticker}: {e}")
            return 0
    
    # TEST 2
    # Get current ratio from database
    def get_current_ratio(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if not company_id:
                return 0
                
            last_year = datetime.now().year - 2
            financial_statement_id = self.db_crud.select_financial_statement(
                company_id, 'balance_sheet', last_year
            )
            if not financial_statement_id:
                return 0
                
            current_assets = self.db_crud.select_financial_data(
                financial_statement_id, 'totalCurrentAssets'
            )
            current_liabilities = self.db_crud.select_financial_data(
                financial_statement_id, 'totalCurrentLiabilities'
            )
            
            if (current_assets is None or current_assets == 'None' or 
                current_liabilities is None or current_liabilities == 'None'):
                return 0
           
            try:
                current_assets = float(current_assets)
                current_liabilities = float(current_liabilities)
            except (ValueError, TypeError):
                return 0
                
            if current_liabilities == 0:
                return 0
                
            return safe_divide(float(current_assets), float(current_liabilities))
        except Exception as e:
            print(f"Error getting current ratio for {self.ticker}: {e}")
            return 0

    # TEST 3
    # Get long term debt to working capital ratio from database
    def get_LTDebt_to_WC(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if not company_id:
                return 0
                
            last_year = datetime.now().year - 2
            financial_statement_id = self.db_crud.select_financial_statement(
                company_id, 'balance_sheet', last_year
            )
            if not financial_statement_id:
                return 0
                
            current_assets = self.db_crud.select_financial_data(
                financial_statement_id, 'totalCurrentAssets'
            )
            current_liabilities = self.db_crud.select_financial_data(
                financial_statement_id, 'totalCurrentLiabilities'
            )
            long_term_debt = self.db_crud.select_financial_data(
                financial_statement_id, 'longTermDebt'
            )
            
            if (current_assets is None or current_assets == 'None' or 
                current_liabilities is None or current_liabilities == 'None' or
                long_term_debt is None or long_term_debt == 'None'):
                return 0
            
            try:
                current_assets = float(current_assets)
                current_liabilities = float(current_liabilities)
                long_term_debt = float(long_term_debt)
            except (ValueError, TypeError):
                return 0

            working_capital = current_assets - current_liabilities
            
            if working_capital == 0:
                return 0

            return safe_divide(float(long_term_debt), float(working_capital))
        except Exception as e:
            print(f"Error calculating LTDebt to WC for {self.ticker}: {e}")
            return 0
    
    # Read dividend record from excel file
    def get_dividend_record_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'No Years']
        
    # GET DGR 3Y from excel file
    def get_DGR_3Y_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 3Y']
        
    # GET DGR 5Y from excel file
    def get_DGR_5Y_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 5Y']
    
    # Get DGR 10Y from excel file
    def get_DGR_10Y_from_excel(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df.at[df.index[df['Symbol'] == self.ticker][0], 'DGR 10Y']

    # TEST 5
    # Compute Earnings Growth
    def earnings_growth_last_10_years(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if not company_id:
                return 0
                
            current_year = datetime.now().year - 1
            
            # Colectează datele pentru ultimii 3 ani
            last_3_years = []
            for year in range(current_year - 3, current_year):
                financial_statement_id = self.db_crud.select_financial_statement(
                    company_id, 'income_statement', year
                )
                if not financial_statement_id:
                    continue
                    
                net_income = self.db_crud.select_financial_data(
                    financial_statement_id, 'netIncome'
                )
                
                if net_income is not None and net_income != 'None':
                    try:
                        last_3_years.append(float(net_income))
                    except (ValueError, TypeError):
                        pass
            
            # Verifică dacă avem date suficiente pentru ultimii 3 ani
            if len(last_3_years) != 3:
                return 0
                
            # Colectează datele pentru primii 3 ani din perioada de 10 ani
            first_3_years = []
            for year in range(current_year - 10, current_year - 7):
                financial_statement_id = self.db_crud.select_financial_statement(
                    company_id, 'income_statement', year
                )
                if not financial_statement_id:
                    continue
                    
                net_income = self.db_crud.select_financial_data(
                    financial_statement_id, 'netIncome'
                )
                
                if net_income is not None and net_income != 'None':
                    try:
                        first_3_years.append(float(net_income))
                    except (ValueError, TypeError):
                        pass
            
            # Verifică dacă avem date suficiente pentru primii 3 ani
            if len(first_3_years) != 3:
                return 0
                
            # Calculează creșterea
            last_3_years_avg = sum(last_3_years) / len(last_3_years)
            first_3_years_avg = sum(first_3_years) / len(first_3_years)
            
            if first_3_years_avg == 0:
                return 0
                
            growth_rate = ((last_3_years_avg / first_3_years_avg) - 1) * 100
            return growth_rate
            
        except Exception as e:
            print(f"Error calculating earnings growth for {self.ticker}: {e}")
            return 0

    # TEST 6
    # Check earnings stability over the past 10 years
    def earnings_stability(self):
        company_id = self.db_crud.select_company(self.ticker)
        if  company_id is None:
            return 0
        
        last_year = datetime.now().year - 2
        for year in range(last_year - 10, last_year):
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', year)
            if financial_statement_id is None: 
                continue
            
            net_income = self.db_crud.select_financial_data(financial_statement_id, 'netIncome')
            if net_income is None:
                continue
            
            if net_income < 0:
                return False
            
        return True

    # Get P/E Ratio using the average earnings per share over the past 3 years
    def compute_PE_ratio(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            past_3_years_earnings = []

            for year in range(datetime.now().year - 5, datetime.now().year - 2):
                financial_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', year)
                if financial_statement_id is None:
                    continue

                net_income = self.db_crud.select_financial_data(financial_statement_id, 'netIncome')
                if net_income is None:
                    continue

                past_3_years_earnings.append(net_income)

            sum = 0
            for earnings in past_3_years_earnings:
                sum += earnings

            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', datetime.now().year - 2)
            if balance_sheet_id is None:
                return 0
            
            shares_outstanding = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if shares_outstanding is None:
                return 0
            
            avg_earnings_per_share = sum / shares_outstanding

            latest_price = self.db_crud.get_last_price(self.ticker)
            if latest_price is None:
                return 0
            
            return safe_divide(float(latest_price), float(avg_earnings_per_share))
        except Exception as e:
            print(f"Error calculating PE ratio for {self.ticker}: {e}")
            return 0

    # TEST 7 - Moderate Price-to-book-ratio
    # 7.1 < 1.5
    def compute_price_to_book_ratio(self):
        # Tangible book value describes the standard definition of book value because it exclude the intangible assets like franchises, brand name, patents and trademarks
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None or company_id == 'None':
                return 0
            
            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', datetime.now().year - 2)
            if balance_sheet_id is None or balance_sheet_id == 'None':
                return 0
            
            total_equity = self.db_crud.select_financial_data(balance_sheet_id, 'totalEquity')
            if total_equity is None or total_equity == 'None':
                return 0
            
            intagible_assets = self.db_crud.select_financial_data(balance_sheet_id, 'intagibleAssets')
            if intagible_assets is None or intagible_assets == 'None':
                return 0
            
            goodwill = self.db_crud.select_financial_data(balance_sheet_id, 'goodwill')
            if goodwill is None or goodwill == 'None':
                goodwill = 0

            shares_outstanding = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if shares_outstanding is None or shares_outstanding == 'None':
                return 0
            
            tangible_book_value = float(total_equity) - float(intagible_assets) - float(goodwill)
            if shares_outstanding == 0:
                return 0
            tangible_book_value_per_share = tangible_book_value / float(shares_outstanding)

            latest_price = self.db_crud.get_last_price(self.ticker)
            if latest_price is None or latest_price == 'None':
                return 0
            
            return safe_divide(float(latest_price), float(tangible_book_value_per_share))
        except Exception as e:
            print(f"Error calculating price to book ratio for {self.ticker}: {e}")
            return 0

    # Graham's suggestion is to multiply the P/E ratio by the price-to-book ratio (which includes intangible assets) and see whether the resulting number is below 22.5
    # 7.2 < 22.5
    def compute_price_to_book_ratio_graham(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None or company_id == 'None':
                return 0

            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', datetime.now().year - 2)
            if balance_sheet_id is None or balance_sheet_id == 'None':
                return 0
            
            total_assets = self.db_crud.select_financial_data(balance_sheet_id, 'totalAssets')
            if total_assets is None or total_assets == 'None':
                return 0    
            
            total_liabilities = self.db_crud.select_financial_data(balance_sheet_id, 'totalLiabilities')
            if total_liabilities is None or total_liabilities == 'None':
                return 0

            shares_outstanding = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if shares_outstanding is None or shares_outstanding == 'None':
                return 0

            book_value = total_assets - total_liabilities

            latest_price = self.db_crud.get_last_price(self.ticker)
            if latest_price is None or latest_price == 'None':
                return 0
            
            market_cap = float(latest_price) * shares_outstanding
            price_to_book_ratio = safe_divide(float(market_cap), float(book_value))

            pe_ratio = self.compute_PE_ratio()

            return float(pe_ratio * price_to_book_ratio)
        except Exception as e:
            print(f"Error calculating price to book ratio for {self.ticker}: {e}")
            return 0

    # Get Dividend Yield
    def get_dividend_yield(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            cashflow_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', datetime.now().year - 2)
            if cashflow_statement_id is None:
                return 0
            
            dividend_payout = self.db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout')
            if dividend_payout is None:
                return 0

            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', datetime.now().year - 2)
            if balance_sheet_id is None:
                return 0
            
            shares_outstanding = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if shares_outstanding is None:
                return 0
            
            if shares_outstanding != 0:
                dividend_per_share = safe_divide(float(dividend_payout), float(shares_outstanding))

                latest_price = self.db_crud.get_last_price(self.ticker)
                if latest_price is None:
                    return 0
        
                return safe_divide(float(dividend_per_share), float(latest_price))
        except Exception as e:
            print(f"Error calculating dividend yield for {self.ticker}: {e}")
            return 0

    # Compute Debt to Total Capital Ratio
    def Debt_to_Total_Capital_Ratio(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            last_year = datetime.now().year - 2
            financial_statement_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', last_year)
            if financial_statement_id is None:
                return 0

            # Get all debt components
            short_term_debt = self.db_crud.select_financial_data(financial_statement_id, 'shortTermDebt')
            long_term_debt = self.db_crud.select_financial_data(financial_statement_id, 'longTermDebt')
            total_equity = self.db_crud.select_financial_data(financial_statement_id, 'totalEquity')

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

            return safe_divide(float(total_debt), float(total_capital))
        except Exception as e:
            print(f"Error calculating Debt to Total Capital Ratio for {self.ticker}: {e}")
            return 0
    
    # ROCE (return on capital employed) = EBIT / (Total Assets - Current Liabilities)
    # Good indicator to evaluate the managerial economic performance
    def compute_ROCE(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            if balance_sheet_id is None:
                return 0
            
            total_assets = self.db_crud.select_financial_data(balance_sheet_id, 'totalAssets')
            if total_assets is None:
                return 0
            
            current_liabilities = self.db_crud.select_financial_data(balance_sheet_id, 'totalCurrentLiabilities')
            if current_liabilities is None:
                return 0
            else:
                denominator = int(total_assets) - int(current_liabilities)
                if denominator == 0:
                    return 0
                
                income_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
                if income_statement_id is None:
                    return 0
                
                ebit = self.db_crud.select_financial_data(income_statement_id, 'ebit')
                if ebit is None:
                    return 0
                
                return safe_divide(float(ebit), float(denominator))
        except Exception as e:
            print(f"Error calculating ROCE for {self.ticker}: {e}")
            return 0
    
    # Get return on equity (ROE)
    def return_on_equity(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            income_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
            if income_statement_id is None:
                return 0
            
            net_income = self.db_crud.select_financial_data(income_statement_id, 'netIncome')
            if net_income is None or net_income == 'None':
                return 0

            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            if balance_sheet_id is None:
                return 0
            
            total_equity = self.db_crud.select_financial_data(balance_sheet_id, 'totalEquity')
            if total_equity is None or total_equity == 'None' or int(total_equity) == 0:
                return 0

            return safe_divide(float(net_income), float(total_equity))
        except Exception as e:
            print(f"Error calculating ROE for {self.ticker}: {e}")
            return 0    
    
    # Get operating income margin
    def operating_income_margin(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            income_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
            if income_statement_id is None:
                return 0
            
            operating_income = self.db_crud.select_financial_data(income_statement_id, 'operatingIncome')
            if operating_income is None:
                return 0
            
            revenue = self.db_crud.select_financial_data(income_statement_id, 'revenue')
            if revenue is None or revenue == 0:
                return 0
            
            return safe_divide(float(operating_income), float(revenue))
        except Exception as e:
            print(f"Error calculating operating income margin for {self.ticker}: {e}")
            return 0

    # Get shares outstanding trend - increase / decrease / consistent decrease
    def ordinary_shares_number_trend_analysis(self):
        company_id = self.db_crud.select_company(self.ticker)
        if company_id is None:
            return 0
        
        current_year = datetime.now().year
        list = []
        balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
        while(balance_sheet_id is not None):
            sharesOutsatnding = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if sharesOutsatnding is not None:
                list.append(sharesOutsatnding)
            current_year -= 1
            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)

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
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            income_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', current_year - 2)
            if income_statement_id is None:
                return 0
            
            net_income = self.db_crud.select_financial_data(income_statement_id, 'netIncome')
            if net_income is None:
                return 0
            
            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            if balance_sheet_id is None:
                return 0
            
            no_shares = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if no_shares is None or no_shares == 0:
                return 0
            
            return safe_divide(float(net_income), float(no_shares))
        except Exception as e:
            print(f"Error calculating EPS for {self.ticker}: {e}")
            return 0
    
    # Get Earnings Payout Ratio
    def earnings_payout_ratio(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            last_year = current_year - 2

            # Get cashflow statement data
            cashflow_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', last_year)
            if cashflow_statement_id is None:
                return 0
            
            dividend_payout = abs(self.db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout'))
            if dividend_payout is None:
                return 0
            
            # Get income statement data
            income_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', last_year)
            if income_statement_id is None:
                return 0
            
            net_income = self.db_crud.select_financial_data(income_statement_id, 'netIncome')
            if net_income is None:
                return 0
                
            return safe_divide(float(dividend_payout), float(net_income))
        except Exception as e:
            print(f"Error calculating earnings payout ratio for {self.ticker}: {e}")
            return 0

    # Get FCF per share
    def get_fcf_per_share(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            cashflow_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)
            if cashflow_statement_id is None:
                return 0

            # Get operating cash flow
            operating_cash_flow = self.db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = self.db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')

            # Get capital expenditures
            capital_expenditures = self.db_crud.select_financial_data(cashflow_statement_id, 'capitalExpenditures')

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
            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            if balance_sheet_id is None:
                return 0
            
            no_shares = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if no_shares is None or no_shares == 'None':
                return 0
                
            try:
                no_shares = int(no_shares)
            except (ValueError, TypeError):
                return 0
                
            return safe_divide(float(free_cash_flow), float(no_shares))
        except Exception as e:
            print(f"Error calculating FCF per share for {self.ticker}: {e}")
            return 0
        
    # Compute FCF Payout Ratio
    def FCF_Payout_Ratio(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            cashflow_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)
            if cashflow_statement_id is None:
                return 0

            # Get operating cash flow
            operating_cash_flow = self.db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = self.db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')
                
            capital_expenditures = self.db_crud.select_financial_data(cashflow_statement_id, 'capitalExpenditures')

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
            dividendPayout = self.db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout')
            if dividendPayout is None or dividendPayout == 'None':
                return 0
                
            try:
                dividendPayout = abs(int(dividendPayout))
            except (ValueError, TypeError):
                return 0
                
            return safe_divide(float(dividendPayout), float(free_cash_flow))
        except Exception as e:
            print(f"Error calculating FCF Payout Ratio for {self.ticker}: {e}")
            return 0
        
    # Compute Operating Cash Flow per Share
    def get_operating_cash_flow_per_share(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            cashflow_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)
            if cashflow_statement_id is None:
                return 0
            
            operating_cash_flow = self.db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = self.db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')

            if operating_cash_flow is None:
                return 0
            
            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            if balance_sheet_id is None:
                return 0

            no_shares = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if no_shares is None or no_shares == 0:
                return 0
            
            return safe_divide(float(operating_cash_flow), float(no_shares))
        except Exception as e:
            print(f"Error calculating operating cash flow per share for {self.ticker}: {e}")
            return 0
        
    # Compute Operating Cash Flow Payout Ratio
    def get_operating_cash_flow_payout_ratio(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            cashflow_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)
            if cashflow_statement_id is None:
                return 0
            
            operating_cash_flow = self.db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = self.db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')
            
            if operating_cash_flow is None or operating_cash_flow == 0:
                return 0
            
            dividendPayout = abs(self.db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout'))
            if dividendPayout is None:
                return 0
            
            return safe_divide(float(dividendPayout), float(operating_cash_flow))
        except Exception as e:
            print(f"Error calculating operating cash flow payout ratio for {self.ticker}: {e}")
            return 0
        
    def dividends_per_share(self):
        try:
            company_id = self.db_crud.select_company(self.ticker)
            if company_id is None:
                return 0
            
            current_year = datetime.now().year
            cashflow_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', current_year - 2)
            if cashflow_statement_id is None:
                return 0
            
            dividendPayout = abs(self.db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout'))
            if dividendPayout is None:
                return 0
            
            balance_sheet_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', current_year - 2)
            if balance_sheet_id is None:
                return 0
            
            no_shares = self.db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
            if no_shares is None or no_shares == 0:
                return 0
            
            return safe_divide(float(dividendPayout), float(no_shares))
        except Exception as e:
            print(f"Error calculating dividends per share for {self.ticker}: {e}")
            return 0