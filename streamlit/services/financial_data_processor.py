import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.db_instance import get_db
import pandas as pd
from financial_analysis import financial_metrics

db_crud = get_db()

def get_income_statement_df(ticker, start_year, end_year):
    company_id = db_crud.select_company(ticker)
    if company_id is None:
        return None

    record_types = [
        "revenue", "grossProfit", "COGS", "researchAndDevelopment", 
        "depreciationAndAmortization", "incomeBeforeTax", 
        "ebit", "netIncome", "interestExpense"
    ]

    raw_data = db_crud.select_financial_data_by_year_range(
        company_id, "income_statement", start_year, end_year, record_types
    )

    if not raw_data:
        return None

    df = pd.DataFrame.from_dict(raw_data, orient="index")
    df.index.name = "Year"
    df.sort_index(inplace=True)

    df = df.applymap(lambda x: round(int(x) / 1_000_000_000, 2) if x not in [None, "None"] else None)

    column_mapping = {
        "revenue": "Revenue",
        "grossProfit": "Gross Profit",
        "COGS": "COGS",
        "researchAndDevelopment": "R&D",
        "depreciationAndAmortization": "D&A",
        "incomeBeforeTax": "Income Before Tax",
        "ebit": "Ebit",
        "netIncome": "Net Income",
        "interestExpense": "Interest Expense"
    }

    df.rename(columns=column_mapping, inplace=True)
    df = df[list(column_mapping.values())]

    df.sort_index(ascending=False, inplace=True)

    return df


def get_balance_sheet_df(ticker, start_year, end_year):
    company_id = db_crud.select_company(ticker)
    if company_id is None:
        return None

    record_types = [
        "totalAssets", "totalCurrentAssets", "inventory", 
        "propertyPlantEquipment", "intagibleAssets", 
        "goodwill", "totalLiabilities", "totalCurrentLiabilities",
        "currentAccountsPayable", "currentDebt", "shortTermDebt", "capitalLeaseObligations", "longTermDebt", 
        "totalEquity", "treasuryStock", "commonStock", "sharesOutstanding"
    ]

    raw_data = db_crud.select_financial_data_by_year_range(
        company_id, "balance_sheet", start_year, end_year, record_types
    )

    if not raw_data:
        return None

    df = pd.DataFrame.from_dict(raw_data, orient="index")
    df.index.name = "Year"
    df.sort_index(inplace=True)

    df = df.applymap(lambda x: round(int(x) / 1_000_000_000, 2) if x not in [None, "None"] else None)

    column_mapping = {
        "totalAssets": "Total Assets",
        "totalCurrentAssets": "Total Current Assets",
        "inventory": "Inventory",
        "propertyPlantEquipment": "Property Plant Equipment",
        "intagibleAssets": "Intangible Assets",
        "goodwill": "Goodwill",
        "totalLiabilities": "Total Liabilities",
        "totalCurrentLiabilities": "Total Current Liabilities",
        "currentAccountsPayable": "Current Accounts Payable",
        "currentDebt": "Current Debt",
        "shortTermDebt": "Short Term Debt",
        "capitalLeaseObligations": "Capital Lease Obligation",
        "longTermDebt": "Long Term Debt",
        "totalEquity": "Total Equity",
        "treasuryStock": "Treasury Stock",
        "commonStock": "Common Stock",
        "sharesOutstanding": "Shares Outstanding"
    }

    df.rename(columns=column_mapping, inplace=True)
    df = df[list(column_mapping.values())]

    df.sort_index(ascending=False, inplace=True)

    return df

def get_cashflow_statement_df(ticker, start_year, end_year):
    company_id = db_crud.select_company(ticker)
    if company_id is None:
        return None

    record_types = [
        "operatingCashFlow", "capitalExpenditures", "cashFlowInvesting", 
        "cashFlowFinancing", "dividendPayout", 
        "dividendPayoutPreferredStock", "changeInOperatingAssets", "changeInOperatingLiabilities"
    ]

    raw_data = db_crud.select_financial_data_by_year_range(
        company_id, "cash_flow_statement", start_year, end_year, record_types
    )

    if not raw_data:
        return None

    df = pd.DataFrame.from_dict(raw_data, orient="index")
    df.index.name = "Year"
    df.sort_index(inplace=True)

    df = df.applymap(lambda x: round(int(x) / 1_000_000_000, 2) if x not in [None, "None"] else None)

    column_mapping = {
        "operatingCashFlow": "Operating Cash Flow",
        "cashFlowInvesting": "Investing Cash Flow",
        "cashFlowFinancing": "Financing Cash Flow",
        "capitalExpenditures": "CAPEX",
        "dividendPayout": "Dividend Payout",
        "dividendPayoutPreferredStock": "Dividend Preferred Stock Payout"
        # "changeInOperatingAssets": "Change in Operating Assets",
        # "changeInOperatingLiabilities": "Change in Operating Liabilities"
    }

    df.rename(columns=column_mapping, inplace=True)
    df = df[list(column_mapping.values())]

    df.sort_index(ascending=False, inplace=True)

    return df

def get_financial_ratios_df(ticker, start_year=2013, end_year=2023):
    try:
        company_id = db_crud.select_company(ticker)
        if company_id is None:
            return None

        data = []
        for year in range(start_year, end_year + 1):
            current_ratio = financial_metrics.calculate_current_ratio(ticker, year)
            pe_ratio = financial_metrics.calculate_price_to_earnings_ratio(ticker, year)
            pb_ratio = financial_metrics.calculate_price_to_book_ratio(ticker, year)
            debt_to_total_capital_ratio = financial_metrics.calculate_Debt_to_Total_Capital_Ratio(ticker, year)
            roce = financial_metrics.calculate_ROCE(ticker, year)
            roe = financial_metrics.calculate_return_on_equity(ticker, year)
            operating_income_margin = financial_metrics.calculate_operating_income_margin(ticker, year)

            data.append({
                "Year": year,
                "P/E Ratio": pe_ratio,
                "P/B Ratio": pb_ratio,
                "Current Ratio": current_ratio,
                "Debt/Total Capital Ratio": debt_to_total_capital_ratio,
                "Operating Income Margin": operating_income_margin,
                "ROE": roe,
                "ROCE": roce
            })

        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error getting financial ratios for {ticker}")
    
