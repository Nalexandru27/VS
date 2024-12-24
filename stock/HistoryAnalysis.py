from stock.Stock import *
import matplotlib.pyplot as plt
import pandas as pd
from database.DatabaseCRUD import DatabaseCRUD

class historyAnalysis:
    def __init__(self, stock: Stock, db_name):
        self.stock = stock
        self.db_crud = DatabaseCRUD(db_name)
    
    def dividends_stability(self):
        dict = {}
        for year in range(2009, 2024):
            # company id
            company_id = self.db_crud.select_company(self.stock.ticker)
            
            # cash flow financial statement id
            cash_flow_financial_statement_id = self.db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
            
            # dividends paid
            dividens_paid = self.db_crud.select_financial_data(cash_flow_financial_statement_id, 'dividendPayout')
            dividens_paid = int(dividens_paid) if dividens_paid and dividens_paid != 'None' else 0
            
            # dividends paid to preferred stock
            dividends_paid_preferred_stock = self.db_crud.select_financial_data(cash_flow_financial_statement_id, 'dividendPayoutPreferredStock')
            dividends_paid_preferred_stock = int(dividends_paid_preferred_stock) if dividends_paid_preferred_stock and dividends_paid_preferred_stock != 'None' else 0
            
            # operating cash flow
            operating_cash_flow = self.db_crud.select_financial_data(cash_flow_financial_statement_id, 'operatingCashFlow')
            operating_cash_flow = int(operating_cash_flow) if operating_cash_flow and operating_cash_flow != 'None' else 0
            
            # capital expenditures
            capex = self.db_crud.select_financial_data(cash_flow_financial_statement_id, 'capitalExpenditures')
            capex = int(capex) if capex and capex != 'None' else 0
            
            # balance sheet financial statement id
            balance_sheet_financial_statement_id = self.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            
            # shares outstanding
            shares_outstanding = self.db_crud.select_financial_data(balance_sheet_financial_statement_id, 'sharesOutstanding')
            shares_outstanding = int(shares_outstanding) if shares_outstanding and shares_outstanding != 'None' else 1
            
            # income statement financial statement id
            income_statement_financial_statement_id = self.db_crud.select_financial_statement(company_id, 'income_statement', year)
            
            # net income
            net_income = self.db_crud.select_financial_data(income_statement_financial_statement_id, 'netIncome')
            net_income = int(net_income) if net_income and net_income != 'None' else 0
            
            # eps per share
            eps_per_share = (net_income - dividends_paid_preferred_stock) / shares_outstanding
            
            # free cash flow per share
            free_cash_flow_per_share = (operating_cash_flow - capex) / shares_outstanding
            
            # dividend per share
            dividend_per_share = dividens_paid / shares_outstanding
            
            dict[year] = {
                'eps_per_share': eps_per_share,
                'free_cash_flow_per_share': free_cash_flow_per_share,
                'dividend_per_share': dividend_per_share
            }      
        
        df = pd.DataFrame.from_dict(dict, orient='index')
        df.index.name = 'fiscal_date_ending'
        df = df.apply(pd.to_numeric, errors='coerce')
        return df


    def plot_dividend_sustainability(self):
        df = self.dividends_stability()
        plot_file = "D:/FacultyYear3/Licenta/VS/outData/dividend_plot.png"

        eps_per_share = df['eps_per_share']
        free_cash_flow_per_share = df['free_cash_flow_per_share']
        dividend_per_share = df['dividend_per_share']
        years = df.index
        plt.figure(figsize=(20,12))

        # Plot each variable with distinct styles
        plt.plot(years, eps_per_share, marker='o', linestyle='-', color='blue', label='EPS Basic')
        plt.plot(years, free_cash_flow_per_share, marker='s', linestyle='--', color='green', label='FCF/share')
        plt.plot(years, dividend_per_share, marker='^', linestyle=':', color='orange', label='Dividends/share')

        # Add data labels with better visibility
        for i, txt in enumerate(eps_per_share):
            plt.text(years[i], eps_per_share.iloc[i] + 0.5, f"{txt:.2f}", fontsize=10, ha='center', 
                    bbox=dict(facecolor='blue', edgecolor='none', alpha=0.7), color='white')

        for i, txt in enumerate(free_cash_flow_per_share):
            plt.text(years[i], free_cash_flow_per_share.iloc[i] - 0.5, f"{txt:.2f}", fontsize=10, ha='center', 
                    bbox=dict(facecolor='green', edgecolor='none', alpha=0.7), color='white')

        for i, txt in enumerate(dividend_per_share):
            plt.text(years[i], dividend_per_share.iloc[i] + 0.5, f"{txt:.2f}", fontsize=10, ha='center', 
                    bbox=dict(facecolor='orange', edgecolor='none', alpha=0.7), color='white')

        # Add chart details
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Value per Share (USD)', fontsize=14)
        plt.title('Dividend Sustainability Analysis (EPS, FCF, Dividends)', fontsize=16, fontweight='bold')
        plt.legend(fontsize=10)

        # Adjust axis ticks and range
        plt.xticks(years, rotation=45, fontsize=10)
        plt.yticks(fontsize=12)

        # Add a grid
        plt.grid(visible=True, linestyle='--', linewidth=0.5, alpha=0.7)

        # Set background colors
        plt.gca().set_facecolor('#f9f9f9')  # Light gray for plot background
        plt.gcf().set_facecolor('white')    # White for figure background

        # Show plot
        plt.tight_layout()

        plt.savefig(plot_file, dpi=400)
        plt.close()

        output_file = f"D:/FacultyYear3/Licenta/VS/outdata/{self.stock.ticker}.xlsx"
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Dividend Data Analysis', index=True)
            worksheet = writer.sheets['Dividend Data Analysis']
            worksheet.insert_image('F2', plot_file, {'x_scale': 0.6, 'y_scale': 0.6})
    
    


