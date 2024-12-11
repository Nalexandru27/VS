from Stock import *
import matplotlib.pyplot as plt

class historyAnalysis:
    def __init__(self, stock: Stock):
        self.stock = stock
        self.income_stmt = stock.get_income_statement()
        self.balance_sheet = stock.get_balance_sheet()
        self.cash_flows = stock.get_cashflow_data() 
    
    def dividendStability(self):
        dividendsPaid, = self.cash_flows['dividendPayout']
        shares_outstanding = self.balance_sheet['sharesOutstanding']
        net_income = self.cash_flows['netIncome']
        operating_cash_flow = self.cash_flows['operatingCF']
        capex = self.cash_flows['capitalExpenditures']

        Dividends_per_share = (dividendsPaid / shares_outstanding).round(2)
        EPS_basic = (net_income / shares_outstanding).round(2)
        FCF__per_share = ((operating_cash_flow - capex) / shares_outstanding).round(2)

        self.cash_flows.index = pd.to_datetime(self.cash_flows.index)
        years = self.cash_flows.index.year.unique()

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


