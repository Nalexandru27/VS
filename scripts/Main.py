import numpy as np
import yfinance as yf
from scripts.Stock import *
from scripts.StockScreener import *
import os
import pandas as pd
import time
import requests
import matplotlib.pyplot as plt
from scripts.EvalutateStock import *


# url = 'https://www.alphavantage.co/query?function=CASH_FLOW&symbol=NUE&apikey=0F4NZKNHX3TGXQ78'
# r = requests.get(url)
# data = r.json()

# annual_reports = data['annualReports']

# dict = {}
# for report in annual_reports:
#     fiscal_date = report['fiscalDateEnding']
#     year = fiscal_date[:4]
#     operating_cashflows = report['operatingCashflow']
#     dividens_paid = report['dividendPayout']
#     dict[year] = [operating_cashflows, dividens_paid]
    
# for year, value in dict.items():
#     print(f"Year: {year}, value: {value}")


# url = 'https://www.alphavantage.co/query?function=CASH_FLOW&symbol=NUE&apikey=0F4NZKNHX3TGXQ78'
# r = requests.get(url)
# data = r.json()

# results = [
#     {
#         'fiscalDateEnding': report['fiscalDateEnding'],
#         'operatingCashflow': report['operatingCashflow'],
#         'dividendPayout': report['dividendPayout'],
#         'capitalExpenditures': report['capitalExpenditures']
#     }
#     for report in data['annualReports']
# ]

# import matplotlib.pyplot as plt

# results = results[::-1]

# # Prepare data for plotting
# years = [result['fiscalDateEnding'][:4] for result in results]  # Extract years
# operating_CF = [float(result['operatingCashflow']) or 0 for result in results]
# dividends_paid = [float(result['dividendPayout']) or 0 for result in results]
# capital_expenditures = [float(result['capitalExpenditures']) or 0 for result in results]
# free_cash_flows = [op_cf - capex for op_cf, capex in zip(operating_CF, capital_expenditures)]
# free_cash_flow_ratios = [(div / fcf) * 100 for div, fcf in zip(dividends_paid, free_cash_flows)]

# operating_cash_flows = [float(x) for x in operating_CF]
# free_cash_flows = [float(x) for x in free_cash_flows]
# free_cash_flow_ratios = [float(x) for x in free_cash_flow_ratios]
# years = [int(year) for year in years]

# # Transform the values to billions
# operating_cash_flows_billion = [ocf / 1_000_000_000 for ocf in operating_cash_flows]
# free_cash_flows_billion = [fcf / 1_000_000_000 for fcf in free_cash_flows]

# # Create figure and axis with a larger size
# fig, ax1 = plt.subplots(figsize=(14, 8))  # Adjusted figsize (14 inches wide by 8 inches tall)

# # Plot Operating Cash Flow and Free Cash Flow on the primary Y-axis
# ax1.plot(years, operating_cash_flows_billion, label='Operating Cash Flow (Billion USD)', marker='o', color='blue')
# ax1.plot(years, free_cash_flows_billion, label='Free Cash Flow (Billion USD)', marker='s', color='green')
# ax1.set_xlabel('Year')
# ax1.set_ylabel('Cash Flows (Billion USD)', color='black')
# ax1.tick_params(axis='y', labelcolor='black')

# # Annotate each point for Operating Cash Flow
# for x, y in zip(years, operating_cash_flows_billion):
#     ax1.text(x, y, f'{y:.2f}', color='blue', fontsize=9, ha='left', va='bottom')

# # Annotate each point for Free Cash Flow
# for x, y in zip(years, free_cash_flows_billion):
#     ax1.text(x, y, f'{y:.2f}', color='green', fontsize=9, ha='left', va='bottom')

# # Add grid for clarity
# ax1.grid(True, linestyle='--', alpha=0.6)

# # Secondary Y-axis for Free Cash Flow Ratio
# ax2 = ax1.twinx()
# ax2.plot(years, free_cash_flow_ratios, label='Free Cash Flow Ratio (%)', marker='x', color='purple')
# ax2.set_ylabel('Free Cash Flow Ratio (%)', color='purple')
# ax2.tick_params(axis='y', labelcolor='purple')

# # Annotate each point for Free Cash Flow Ratio
# for x, y in zip(years, free_cash_flow_ratios):
#     ax2.text(x, y, f'{y:.1f}%', color='purple', fontsize=9, ha='left', va='bottom')

# # Combine legends from both axes
# lines_1, labels_1 = ax1.get_legend_handles_labels()
# lines_2, labels_2 = ax2.get_legend_handles_labels()
# ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

# # Set title
# plt.title('Operating Cash Flow, Free Cash Flow, and Ratios Over Time')

# # Display the plot
# plt.show()

# current_date = datetime.now().strftime("%Y-%m-%d")
# file_name = f"./outData/companies_screened_{current_date}.xlsx"
# def create_excel_file():
#     if os.path.exists(FILE_PATH_1):
#         print("File found, proceeding to read it.")
#         df = pd.read_excel(FILE_PATH_1)
#         data = df.iloc[1:len(df)]
#         groups = 12
#         rows = len(data)
#         prev = 0
#         screener = StockScreener()
#         for i in range(groups):
#             if i == groups - 1:
#                 next = (i + 1) * (rows // groups) + rows % groups
#             else:
#                 next = (i + 1) * (rows // groups)
#             tickers = data.iloc[prev:next, 0].tolist()
#             screening_start_time = time.time()
#             screener.screen_stocks(tickers)
#             screening_end_time = time.time()
#             prev = next
#             print(f"Screening {i+1} took: {(screening_end_time - screening_start_time)/60:.2f} minutes")
#             print(f"Sleeping for 60 seconds")
#             time.sleep(60)
#         for i in range(2):
#             print(f"Exporting in {2-i} minutes")
#             time.sleep(60)
#         screener.export_results_to_excel_file(file_name)
#     else:
#         print("File not found. Check the path:", FILE_PATH_1)
# create_excel_file()

# date = datetime.now().strftime("%Y-%m-%d")
# file_name = f"./outData/companies_evaluated_{date}.txt"
# companies = ['GPC', 'ADM']
# for company in companies:
#     stock = Stock(company)
#     evaluator = evaluateStock(stock, FILE_PATH_1)
#     evaluator.export_results_to_text_file(file_name)

# Cash Flow Analysis for last 15 years
def get_cashflow_data(stock):
    url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={stock}&apikey=demo'
    r = requests.get(url)
    data = r.json()
    annual_reports = data['annualReports']
    i = 0
    cashflow_data = {}
    for report in annual_reports:
        if i < 15:
            date = report['fiscalDateEnding']
            cashflow_data[date] = {
                'operatingCF': report['operatingCashflow'],
                'CashFlowInvestment': report['cashflowFromInvestment'],
                'CashFlowFinancing': report['cashflowFromFinancing'],
                'dividendPayout': report['dividendPayout'],
                'capitalExpenditures': report['capitalExpenditures'],
                'netIncome': report['netIncome']
            }
            i += 1
        else:
            break
    df = pd.DataFrame.from_dict(cashflow_data, orient='index')
    df = df.index.name = 'fiscal_date_ending'
    return df
    

def get_income_statement(stock):
    url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={stock}&apikey=demo'
    r = requests.get(url)
    data = r.json()
    annual_reports = data['annualReports']
    i = 0
    income_statement = {}
    for report in annual_reports:
        if i < 15:
            date = report['fiscalDateEnding']
            income_statement[date] = {
                'revenue': report['totalRevenue'],
                'grossProfit': report['grossProfit'],
                'ebit': report['ebit'],
                'operatingIncome': report['operatingIncome'],
                'cogs': report['costofGoodsAndServicesSold'],
                'netIncomeFromContinuingOps': report['netIncomeFromContinuingOperations'],
                'researchAndDevelopment': report['researchAndDevelopment']
            }
            i += 1
        else:
            break
    df = pd.DataFrame.from_dict(income_statement, orient='index')
    df.index.name = 'fiscal_date_ending'
    return df

df = get_income_statement('IBM')
df.to_excel('IBM_income_statement.xlsx')

def get_balance_sheet(stock):
    url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={stock}&apikey=demo'
    r = requests.get(url)
    data = r.json()
    annual_reports = data['annualReports']
    i = 0
    balance_sheet = {}
    for report in annual_reports:
        if i < 15:
            date = report['fiscalDateEnding']
            balance_sheet[date] = {
                'totalAssets': report['totalAssets'],
                'totalCurrentAssets': report['totalCurrentAssets'],
                'intagibleAssets': report['intangibleAssets'],
                'totalLiabilities': report['totalLiabilities'],
                'totalCurrentLiabilities': report['totalCurrentLiabilities'],
                'currentDebt': report['currentDebt'],
                'capitalLeaseObligations': report['capitalLeaseObligations'],
                'longTermDebt': report['longTermDebt'],
                'sharesOutstanding': report['commonStockSharesOutstanding'],
                'totalEquity': report['totalShareholderEquity']
            }
            i += 1
        else:
            break
    df = pd.DataFrame.from_dict(balance_sheet, orient='index')
    df.index.name = 'fiscal_date_ending'
    return df

# df = get_balance_sheet('IBM')
# df.to_excel('IBM_balance_sheet.xlsx')
# print(df)

# url = 'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol=IBM&apikey=demo'
# r = requests.get(url)
# data = r.json()

# print(data)