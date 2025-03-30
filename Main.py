from stock.Stock import *
from stock.EvalutateStock import *
from database.PopulateDB import PopulateDB
from HistoryAnalysis.DividendAnalysis import dividendAnalysis
from PriceEstimators.PriceEstimationEarnings import PERatioEstimator
from PriceEstimators.PriceEstimationEBIT import PEBITRatioEstimator
from PriceEstimators.PriceEstimationOpCF import PriceOpCFRatioEstimator
from PriceEstimators.PriceEstimationFCF import PriceFCFRatioEstimator
from PriceEstimators.PriceEstimationDividend import PriceDividendRatioEstimator
from stock.StockScreener import StockScreener
import time, datetime
from utils.Constants import DIVIDEND_SHEET_URL, DIVIDEND_COMPANY_FILE_PATH, FILTERED_DIVIDEND_COMPANY_FILE_PATH, HISTORICAL_PRICE_SHEET_URL, PRICE_HISTORY_FILE_PATH, DAILY_PRICE_SHEET_URL, PRICE_DAILY_FILE_PATH, CLEANED_PRICE_DAILY_FILE_PATH
from utils.SaveDividendData import SaveDocsData
from datetime import datetime
import atexit
from database.DatabaseConnection import db_connection

def inspect_dividend_data():
    url = 'https://www.alphavantage.co/query?function=DIVIDENDS&symbol=CCi&apikey=WYGPKB8T21WMM6LO'
    r = requests.get(url)
    data = r.json()

    print(data)

def inspect_income_statement_data():
    url = 'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=WMT&apikey=WYGPKB8T21WMM6LO'
    r = requests.get(url)
    data = r.json()
    annual_reports = data['annualReports']
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
                'depreciationAndAmortization': report['depreciationAndAmortization'],
                'researchAndDevelopment': report['researchAndDevelopment']
            }
            i += 1
        else:
            break
    df = pd.DataFrame.from_dict(income_statement, orient='index')
    df.index.name = 'fiscal_date_ending'
    df = df.apply(pd.to_numeric, errors='coerce')
    return df

# Get balance sheet
def get_balance_sheet():
    url = 'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol=IBM&apikey=demo'
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
    df = df.apply(pd.to_numeric, errors='coerce')
    return df

income_stmt = get_income_statement()
balance_sheet = get_balance_sheet()
cash_flows = get_cashflow_data()

# print(cash_flows)

dividendsPaid = cash_flows['dividendPayout']
shares_outstanding = balance_sheet['sharesOutstanding']
net_income = cash_flows['netIncome']
operating_cash_flow = cash_flows['operatingCF']
capex = cash_flows['capitalExpenditures']

Dividends_per_share = (dividendsPaid / shares_outstanding).round(2)
EPS_basic = (net_income / shares_outstanding).round(2)
FCF__per_share = ((operating_cash_flow - capex) / shares_outstanding).round(2)

cash_flows.index = pd.to_datetime(cash_flows.index)
years = cash_flows.index.year

# Plotting
plt.figure(figsize=(16,10))

# Plot each variable with distinct styles
plt.plot(years, EPS_basic, marker='o', linestyle='-', color='blue', label='EPS Basic')
plt.plot(years, FCF__per_share, marker='s', linestyle='--', color='green', label='FCF/share')
plt.plot(years, Dividends_per_share, marker='^', linestyle=':', color='orange', label='Dividends/share')

# Add data labels with better visibility
for i, txt in enumerate(EPS_basic):
    plt.text(years[i], EPS_basic.iloc[i] + 0.5, f"{txt:.2f}", fontsize=10, ha='center', 
             bbox=dict(facecolor='blue', edgecolor='none', alpha=0.7), color='white')

for i, txt in enumerate(FCF__per_share):
    plt.text(years[i], FCF__per_share.iloc[i] - 0.5, f"{txt:.2f}", fontsize=10, ha='center', 
             bbox=dict(facecolor='green', edgecolor='none', alpha=0.7), color='white')

for i, txt in enumerate(Dividends_per_share):
    plt.text(years[i], Dividends_per_share.iloc[i] + 0.5, f"{txt:.2f}", fontsize=10, ha='center', 
             bbox=dict(facecolor='orange', edgecolor='none', alpha=0.7), color='white')

# Add chart details
plt.xlabel('Year', fontsize=12)
plt.ylabel('Value per Share (USD)', fontsize=12)
plt.title('Dividend Sustainability Analysis (EPS, FCF, Dividends)', fontsize=16, fontweight='bold')
plt.legend(fontsize=10)

# Adjust axis ticks and range
plt.xticks(years, rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# Add a grid
plt.grid(visible=True, linestyle='--', linewidth=0.5, alpha=0.7)

# Set background colors
plt.gca().set_facecolor('#f9f9f9')  # Light gray for plot background
plt.gcf().set_facecolor('white')    # White for figure background

# Show plot
plt.tight_layout()
plt.show()


