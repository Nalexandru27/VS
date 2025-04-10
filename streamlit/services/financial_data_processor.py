from services.db_instance import get_db
import pandas as pd

def get_income_statement_df(ticker, start_year, end_year):
    db_crud = get_db()
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
    
