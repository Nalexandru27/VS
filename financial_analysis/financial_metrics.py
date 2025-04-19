from database.DatabaseCRUD import DatabaseCRUD
import os
import pandas as pd
from utils.Constants import FILTERED_DIVIDEND_COMPANY_FILE_PATH
from datetime import datetime, timedelta
from utils.SafeDivide import safe_divide
from datetime import datetime

db_crud = DatabaseCRUD()

def get_last_trading_day(year):
    last_day = datetime(year, 12, 31)

    while last_day.weekday() > 4:
        last_day -= timedelta(days=1)

    return last_day.strftime('%Y-%m-%d')

def calculate_market_cap(ticker, year):
        try:
            date = get_last_trading_day(year)

            price = db_crud.get_price(ticker, date)
            if price is None:
                return None
                
            company_id = db_crud.select_company(ticker)
            if not company_id:
                return None
                
            balance_sheet_id = db_crud.select_financial_statement(
                company_id, 'balance_sheet', year
            )
            if not balance_sheet_id:
                return None
                
            shares_outstanding = db_crud.select_financial_data(
                balance_sheet_id, 'sharesOutstanding'
            )
            
            if shares_outstanding is None:
                return None
                
            try:
                shares_outstanding = float(shares_outstanding)
            except (ValueError, TypeError):
                return None
                
            return price * shares_outstanding
        except Exception as e:
            print(f"Error getting market cap for {ticker}: {e}")
            return None
        
def calculate_current_ratio(ticker, year):
        try:
            company_id = db_crud.select_company(ticker)
            if not company_id:
                return None
                
            financial_statement_id = db_crud.select_financial_statement(
                company_id, 'balance_sheet', year
            )
            if not financial_statement_id:
                return None
                
            current_assets = db_crud.select_financial_data(
                financial_statement_id, 'totalCurrentAssets'
            )
            current_liabilities = db_crud.select_financial_data(
                financial_statement_id, 'totalCurrentLiabilities'
            )
            
            if (current_assets is None or 
                current_liabilities is None):
                return None
           
            try:
                current_assets = float(current_assets)
                current_liabilities = float(current_liabilities)
            except (ValueError, TypeError):
                return None
                
            if current_liabilities == 0:
                return None
            
            return safe_divide(float(current_assets), float(current_liabilities))
        except Exception as e:
            print(f"Error getting current ratio for {ticker}: {e}")
            return None
        
def get_dividend_record_from_excel(ticker):
        if os.path.exists(FILTERED_DIVIDEND_COMPANY_FILE_PATH):
            df = pd.read_csv(FILTERED_DIVIDEND_COMPANY_FILE_PATH)
            return df.at[df.index[df['Symbol'] == ticker][0], 'No Years']
        
def calculate_dividend_record(ticker, year):
     current_year = datetime.now().year
     dividend_record = get_dividend_record_from_excel(ticker)
     difference_of_years = current_year - year
     return dividend_record - difference_of_years

def get_dividend_yield(ticker, year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None
            
        cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
        if cashflow_statement_id is None:
            return None
            
        dividend_payout = db_crud.select_financial_data(cashflow_statement_id, 'dividendPayout')
        if dividend_payout is None or dividend_payout == "None":
            return None

        balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', year)
        if balance_sheet_id is None:
            return None

        shares_outstanding = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
        if shares_outstanding is None or shares_outstanding == "None":
            return None

        try:
            dividend_payout = float(dividend_payout)
            shares_outstanding = float(shares_outstanding)
        except (ValueError, TypeError):
            return None
        
        dividend_per_share = safe_divide(dividend_payout, shares_outstanding)
        
        latest_price = db_crud.get_last_price(ticker)
        if latest_price is None:
            return None
        
        return safe_divide(float(dividend_per_share), float(latest_price))
    except Exception as e:
        print(f"Error calculating dividend yield for {ticker}: {e}")
        return None

def calculate_EPS(ticker, year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None
            
        income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
        if income_statement_id is None:
            return None
            
        net_income = db_crud.select_financial_data(income_statement_id, 'netIncome')
        if net_income is None or net_income == "None":
            return None
            
        balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', year)
        if balance_sheet_id is None:
            return None
            
        no_shares = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
        if no_shares is None or no_shares == "None" or no_shares == 0:
            return None
            
        return safe_divide(float(net_income), float(no_shares))
    except Exception as e:
        print(f"Error calculating EPS for {ticker}: {e}")
        return None
    
def calculate_FCF_per_share(ticker, year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None
            
        cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
        if cashflow_statement_id is None:
            return None

        # Get operating cash flow
        operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
        if operating_cash_flow is None or operating_cash_flow == 'None':
            operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')

        # Get capital expenditures
        capital_expenditures = db_crud.select_financial_data(cashflow_statement_id, 'capitalExpenditures')

        # Check for None values
        if operating_cash_flow is None or capital_expenditures is None:
            return None
                
        # Convert to integers
        try:
            operating_cash_flow = float(operating_cash_flow)
            capital_expenditures = float(capital_expenditures)
        except (ValueError, TypeError):
            return None

        free_cash_flow = operating_cash_flow - capital_expenditures

        # Get shares outstanding
        balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', year)
        if balance_sheet_id is None:
            return None
            
        no_shares = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
        if no_shares is None:
            return None
                
        try:
            no_shares = int(no_shares)
        except (ValueError, TypeError):
            return None
                
        return safe_divide(float(free_cash_flow), float(no_shares))
    except Exception as e:
        print(f"Error calculating FCF per share for {ticker}: {e}")
        return None
    
def calculate_operating_cash_flow_per_share(ticker, year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None
            
        cashflow_statement_id = db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
        if cashflow_statement_id is None:
            return None
            
        operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFlow')
        if operating_cash_flow is None or operating_cash_flow == "None":
            operating_cash_flow = db_crud.select_financial_data(cashflow_statement_id, 'operatingCashFow')

        if operating_cash_flow is None or operating_cash_flow == "None":
            return None
            
        balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', year)
        if balance_sheet_id is None:
            return None

        no_shares = db_crud.select_financial_data(balance_sheet_id, 'sharesOutstanding')
        if no_shares is None or no_shares == 0 or no_shares == "None":
            return None
            
        return safe_divide(float(operating_cash_flow), float(no_shares))
    except Exception as e:
        print(f"Error calculating operating cash flow per share for {ticker}: {e}")
        return None
    
def calculate_operating_income_margin(ticker, year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None
            
        income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
        if income_statement_id is None:
            return None
            
        operating_income = db_crud.select_financial_data(income_statement_id, 'operatingIncome')
        if operating_income is None:
            return None
            
        revenue = db_crud.select_financial_data(income_statement_id, 'revenue')
        if revenue is None or revenue == 0:
            return None
            
        return safe_divide(float(operating_income), float(revenue))
    except Exception as e:
        print(f"Error calculating operating income margin for {ticker}: {e}")
        return None
    
def calculate_return_on_equity(ticker, year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None
            
        income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
        if income_statement_id is None:
            return None
            
        net_income = db_crud.select_financial_data(income_statement_id, 'netIncome')
        if net_income is None:
            return None

        balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', year)
        if balance_sheet_id is None:
            return None
            
        total_equity = db_crud.select_financial_data(balance_sheet_id, 'totalEquity')
        if total_equity is None or float(total_equity) == 0:
            return None

        return safe_divide(float(net_income), float(total_equity))
    except Exception as e:
        print(f"Error calculating ROE for {ticker}: {e}")
        return None

def calculate_ROCE(ticker, year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None
            
        balance_sheet_id = db_crud.select_financial_statement(company_id, 'balance_sheet', year)
        if balance_sheet_id is None:
            return None
            
        total_assets = db_crud.select_financial_data(balance_sheet_id, 'totalAssets')
        if total_assets is None or total_assets == "None":
            return None

        current_liabilities = db_crud.select_financial_data(balance_sheet_id, 'totalCurrentLiabilities')
        if current_liabilities is None or current_liabilities == "None":
            return None

        income_statement_id = db_crud.select_financial_statement(company_id, 'income_statement', year)
        if income_statement_id is None:
            return None

        ebit = db_crud.select_financial_data(income_statement_id, 'ebit')
        if ebit is None or ebit == "None":
            return None

        try:
            total_assets = float(total_assets)
            current_liabilities = float(current_liabilities)
            ebit = float(ebit)
        except (ValueError, TypeError):
            return None

        denominator = total_assets - current_liabilities
        if denominator == 0:
            return None

        return safe_divide(ebit, denominator)
    except Exception as e:
        print(f"Error calculating ROCE for {ticker}: {e}")
        return None
    
def calculate_Debt_to_Total_Capital_Ratio(ticker, year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None
            
        financial_statement_id = db_crud.select_financial_statement(company_id, 'balance_sheet', year)
        if financial_statement_id is None:
            return None

        current_debt = db_crud.select_financial_data(financial_statement_id, 'currentDebt')
        short_term_debt = db_crud.select_financial_data(financial_statement_id, 'shortTermDebt')
        long_term_debt = db_crud.select_financial_data(financial_statement_id, 'longTermDebt')
        total_equity = db_crud.select_financial_data(financial_statement_id, 'totalEquity')

        try:
            current_debt = 0.0 if current_debt is None else float(current_debt)
            short_term_debt = 0.0 if short_term_debt is None else float(short_term_debt)
            long_term_debt = 0.0 if long_term_debt is None else float(long_term_debt)
            total_equity = 0.0 if total_equity is None else float(total_equity)
        except (ValueError, TypeError):
            return None

        if any(x is None for x in [current_debt, short_term_debt, long_term_debt, total_equity]):
            return None

        total_debt = short_term_debt + long_term_debt + current_debt
        total_capital = total_debt + total_equity

        return safe_divide(total_debt, total_capital)
    except Exception as e:
        print(f"Error calculating Debt to Total Capital Ratio for {ticker}: {e}")
        return None
    
def get_dividend_payouts(ticker, start_year, end_year):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            print(f"No company found with this ticker {ticker}")
            return None

        record_type = "dividendPayout"
        record_types = [record_type] if isinstance(record_type, str) else record_type

        dividend_payouts_df = db_crud.select_financial_data_by_year_range(
            company_id, "cash_flow_statement", start_year, end_year, record_types)

        if dividend_payouts_df is None:
            print(f"No data found for dividends payout for company {ticker} with id {company_id}")
            return None

        return dividend_payouts_df
    except Exception as e:
        print(f"Could not retrieve the dividend payouts for prediction because: {e}")

def calculate_dividend_annual_growth_rate(ticker, start_year, end_year):
    try:
        dividend_payout_df = get_dividend_payouts(ticker, start_year, end_year)
        if dividend_payout_df is None:
            return None

        first_year_data = dividend_payout_df.get(start_year)
        if first_year_data is None:
            return None
        
        previous_year_dividend_payout = first_year_data.get('dividendPayout')
        if previous_year_dividend_payout is None:
            return None
        
        try:
            previous_year_dividend_payout = float(previous_year_dividend_payout)
        except (ValueError, TypeError):
            return None
        
        dividend_annual_growth_dict = {}

        for year, data in dividend_payout_df.items():
                if year == start_year:
                    continue

                current_dividend_payout = data.get('dividendPayout')
                if current_dividend_payout is None:
                    dividend_annual_growth = None
                else:
                    try:
                        current_dividend_payout = float(current_dividend_payout)
                    except (ValueError, TypeError):
                        dividend_annual_growth = None

                if current_dividend_payout is None or previous_year_dividend_payout is None:
                    dividend_annual_growth = None
                elif previous_year_dividend_payout != 0:
                    dividend_annual_growth = round((current_dividend_payout - previous_year_dividend_payout) / previous_year_dividend_payout, 2)
                    dividend_annual_growth_dict[year] = dividend_annual_growth
                if current_dividend_payout is not None:
                    previous_year_dividend_payout = current_dividend_payout

        return dividend_annual_growth_dict
    except Exception as e:
        print(f"Cannot compute dividend annual growth rate because: {e}")
        return None


