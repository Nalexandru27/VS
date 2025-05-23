from stock.Stock import *
import matplotlib.pyplot as plt
import pandas as pd
from database.DatabaseCRUD import DatabaseCRUD
from xlsxwriter import Workbook
import os

class dividendAnalysis:
    def __init__(self, stock: Stock):
        self.stock = stock
        self.plots_dir = "D:/Facultate/An 3/Licenta/Lucrare Licenta/VS/outData/dividend_analysis"
        os.makedirs(self.plots_dir, exist_ok=True)
    
    def dividends_stability(self, start_year, end_year):
        dict = {}
        for year in range(start_year, end_year + 1):
            # company id
            company_id = self.stock.db_crud.select_company(self.stock.ticker)
            if company_id is None:
                print(f"Company {self.stock.ticker} not found in the database")
                return None
            
            # cash flow financial statement id
            cash_flow_financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'cash_flow_statement', year)
            if cash_flow_financial_statement_id is None:
                print(f"Financial statement for {self.stock.ticker} not found in the database")
                return None
            
            # dividends paid
            dividens_paid = self.stock.db_crud.select_financial_data(cash_flow_financial_statement_id, 'dividendPayout')
            if dividens_paid is None or dividens_paid == 'None':
                return None
            dividens_paid = int(dividens_paid)
            
            # dividends paid to preferred stock
            dividends_paid_preferred_stock = self.stock.db_crud.select_financial_data(cash_flow_financial_statement_id, 'dividendPayoutPreferredStock')
            dividends_paid_preferred_stock = int(dividends_paid_preferred_stock) if dividends_paid_preferred_stock and dividends_paid_preferred_stock != 'None' else 0
            
            # operating cash flow
            operating_cash_flow = self.stock.db_crud.select_financial_data(cash_flow_financial_statement_id, 'operatingCashFlow')
            if operating_cash_flow is None or operating_cash_flow == 'None':
                operating_cash_flow = self.stock.db_crud.select_financial_data(cash_flow_financial_statement_id, 'operatingCashFow')
            
            operating_cash_flow = int(operating_cash_flow) if operating_cash_flow and operating_cash_flow != 'None' else 0

            # capital expenditures
            capex = self.stock.db_crud.select_financial_data(cash_flow_financial_statement_id, 'capitalExpenditures')
            capex = int(capex) if capex and capex != 'None' else 0
            
            # balance sheet financial statement id
            balance_sheet_financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'balance_sheet', year)
            
            # shares outstanding
            shares_outstanding = self.stock.db_crud.select_financial_data(balance_sheet_financial_statement_id, 'sharesOutstanding')
            if shares_outstanding is None or shares_outstanding == 'None':
                return None
            shares_outstanding = int(shares_outstanding)
            
            # income statement financial statement id
            income_statement_financial_statement_id = self.stock.db_crud.select_financial_statement(company_id, 'income_statement', year)
            
            # net income
            net_income = self.stock.db_crud.select_financial_data(income_statement_financial_statement_id, 'netIncome')
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


    def plot_dividend_sustainability(self, start_year, end_year):
        print(f"Plotting dividend sustainability for {self.stock.ticker} from {start_year} to {end_year}")
        df = self.dividends_stability(start_year=start_year, end_year=end_year)
        if df is None:
            print(f"Error getting the necessary dividend data for {self.stock.ticker} => skipping plot")
            return 0

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
            plt.text(years[i], eps_per_share.iloc[i], f"{txt:.2f}", fontsize=10, ha='center', 
                    bbox=dict(facecolor='blue', edgecolor='none', alpha=0.7), color='white')

        for i, txt in enumerate(free_cash_flow_per_share):
            plt.text(years[i], free_cash_flow_per_share.iloc[i], f"{txt:.2f}", fontsize=10, ha='center', 
                    bbox=dict(facecolor='green', edgecolor='none', alpha=0.7), color='white')

        for i, txt in enumerate(dividend_per_share):
            plt.text(years[i], dividend_per_share.iloc[i], f"{txt:.2f}", fontsize=10, ha='center', 
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

        import io
        img_data = io.BytesIO()
        
        try:
            plt.savefig(img_data, format='png', dpi=400)
            img_data.seek(0)  # Move to the start of the BytesIO buffer
        except Exception as e:
            print(f"Error creating plot for {self.stock.ticker}: {e}")
            return
        
        plt.close()

        # Create Excel file with embedded image
        output_file = os.path.join(self.plots_dir, f"{self.stock.ticker}_analysis.xlsx")
        
        try:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Dividend Data Analysis', index=True)
                workbook = writer.book
                worksheet = writer.sheets['Dividend Data Analysis']
                
                # Insert image from the memory buffer
                worksheet.insert_image('F2', f"{self.stock.ticker}_plot.png", {'image_data': img_data, 'x_scale': 0.6, 'y_scale': 0.6})
            
            print(f"Successfully created Excel file with embedded plot: {os.path.abspath(output_file)}")
        except Exception as e:
            print(f"Error creating Excel file for {self.stock.ticker}: {e}")


