from Stock import *

class StockScreener:
    def __init__(self):
        self.result = {}

    def validate_criterias(self ,stock: Stock):
        try:
            # Check Market Cap
            if not stock.check_market_cap():
                print(f"-->{stock.ticker} failed the test 'MarketCap'")
                return False

            # Check Current Ratio
            if not stock.check_current_ratio():
                print(f"-->{stock.ticker} failed the test 'CurrentRatio'")
                return False

            # Check Long-Term Debt to Working Capital
            if not stock.check_LTDebt_To_WC():
                print(f"-->{stock.ticker} failed the test 'LTDebtToWC'")
                return False

            # Check Earnings Stability
            if not stock.check_earnings_stability():
                print(f"-->{stock.ticker} failed the test 'Earnings Stability'")
                return False

            # Check Dividend Record
            if not stock.check_dividend_record():
                print(f"-->{stock.ticker} failed the test 'Dividend Record'")
                return False

            # Check Earnings Growth
            if not stock.check_earnings_growth():
                print(f"-->{stock.ticker} failed the test 'Earnings Growth'")
                return False

            # Check P/E Ratio
            if not stock.check_PE_ratio():
                print(f"-->{stock.ticker} failed the test 'P/E Ratio'")
                return False

            # Check Price_To_Book_Ratio normal and using Graham's formula
            if not stock.check_price_to_book_ratio_graham() and not stock.check_price_to_book_ratio():
                print(f"-->{stock.ticker} failed the test 'Price_To_Book_Ratio'(normal and Graham's)")
                return False

            # All tests passed
            return True
        except Exception as e:
            print(f"Error occured during screening: {e}")
            return False
    
    def screen_stocks(self, tickers):
        self.result = {}
        for ticker in tickers:
            print(f"Screening {ticker}...")
            stock = Stock(ticker)
            self.result[ticker] = self.validate_criterias(stock)
        print("\n")
        print("Screening done. Results are ready!")
        print("\n")

    def inspect_results_of_screening(self):
        for ticker, value in self.result.items():
            if value:
                print(f'{ticker} passed all tests')
                stock = Stock(ticker)
                stock.print_results()
            else:
                print(f"{ticker} did not pass all the test")
                print("\n")