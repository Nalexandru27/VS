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
            
            # Check Dividend Record
            if not stock.check_dividend_record():
                print(f"-->{stock.ticker} failed the test 'Dividend Record'")
                return False

            # Check P/E Ratio
            if not stock.check_PE_ratio():
                print(f"-->{stock.ticker} failed the test 'P/E Ratio'")
                return False

            # Check Price_To_Book_Ratio normal and using Graham's formula
            if not stock.check_price_to_book_ratio_graham() and not stock.check_price_to_book_ratio():
                print(f"-->{stock.ticker} failed the test 'Price_To_Book_Ratio'(normal and Graham's)")
                return False

            # Check Earnings Stability
            # if not stock.check_earnings_stability():
            #     print(f"-->{stock.ticker} failed the test 'Earnings Stability'")
            #     return False

            # # Check Earnings Growth
            # if not stock.check_earnings_growth():
            #     print(f"-->{stock.ticker} failed the test 'Earnings Growth'")
            #     return False

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
        print("Screening done.")
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
            
    def export_results(self, file_name):
        print(f"Exporting results to {file_name}...")
        with open(file_name, 'w') as file:
            for ticker, value in self.result.items():
                if value:
                    file.write(f'{ticker} passed all tests\n')
                    stock = Stock(ticker)
                    data = self.stock_data(stock)
                    for key, value in data.items():
                        file.write(f'{key}: {value}\n')
                    file.write("----------------------\n")
            print(f"Results exported to {file_name}")

    def stock_data(self,stock):
        date = {}
        date['Market Cap'] = f"{stock.get_market_cap()/BILLION_DIVISION:.2f}B"
        date['Current Ratio'] = f"{stock.get_current_ratio():.2f}"
        date['LTDebtToWC'] = f"{stock.calculate_LTDebt_to_WC():.2f}"
        date['Dividend Record'] = stock.count_consecutive_years_of_dividend_increase()
        date['P/E Ratio'] = f"{stock.compute_PE_ratio():.2f}"
        date['Price-to-book ratio'] = f"{stock.compute_price_to_book_ratio():.2f}"
        date["Graham's price-to-book ratio"] = f"{stock.compute_price_to_book_ratio_graham():.2f}"
        # date['Earnings Stability'] = stock.check_earnings_stability()
        # date['Earnings Growth'] = stock.earnings_growth_last_10_years()
        return date