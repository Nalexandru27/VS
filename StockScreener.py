from concurrent.futures import ThreadPoolExecutor
from Stock import *
import pandas as pd
import CreateExcelFile

class StockScreener:
    def __init__(self):
        self.result = {}

    def validate_criterias(self, stock: Stock):
        try:
            # Check Market Cap
            if not stock.check_market_cap():
                print(f"-->{stock.ticker} failed the test 'MarketCap'")
                return False

            # Check Current Ratio
            if stock.yf.info["sector"] != "Utilities":
                if not stock.check_current_ratio():
                    print(f"-->{stock.ticker} failed the test 'CurrentRatio'")
                    return False
            else:
                print(f"{stock.ticker} is a utility company. Current ratio test skipped")
            
            # Check Long-Term Debt to Working Capital
            if not stock.check_LTDebt_To_WC():
                print(f"-->{stock.ticker} failed the test 'LTDebtToWC'")
                return False
            
            # Check Dividend Record
            # if not stock.check_dividend_record():
            #     print(f"-->{stock.ticker} failed the test 'Dividend Record'")
            #     return False

            # Check P/E Ratio
            if not stock.check_PE_ratio():
                print(f"-->{stock.ticker} failed the test 'P/E Ratio'")
                return False

            # Check Price_To_Book_Ratio normal and using Graham's formula
            if (not stock.check_price_to_book_ratio_graham() and not stock.check_price_to_book_ratio()):
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

        def process_ticker(ticker):
            print(f"Screening {ticker}...")
            stock = Stock(ticker)
            self.result[ticker] = self.validate_criterias(stock)
        
        with ThreadPoolExecutor() as executor:
            executor.map(process_ticker, tickers)

        print("\nScreening done.\n")

    def inspect_results_of_screening(self):
        for ticker, value in self.result.items():
            if value:
                print(f'{ticker} passed all tests')
                stock = Stock(ticker)
                stock.print_results()
            else:
                print(f"{ticker} did not pass all the test")
                print("\n")
            
    def export_results_to_text_file(self, file_name):
        print(f"Exporting results to {file_name}...")
        if not self.result:
            print("No results to export. Ensure the screening process was completed successfully.")
            return
        
        def process_ticker(ticker):
            try:
                if self.result[ticker]:
                    stock = Stock(ticker)
                    data = self.stock_data(stock)
                    result = f"{ticker} passed all tests\n"
                    result += "\n".join([f"{key}: {value}" for key, value in data.items()])
                    result += "\n----------------------\n"
                    return result
                return ""
            except Exception as e:
                return f"Error processing {ticker}: {e}\n"

        try:
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_ticker, ticker) for ticker in self.result]
                results = [future.result() for future in futures]

            with open(file_name, 'w') as file:
                file.writelines(results)

            print(f"Results exported to {file_name}")
        except Exception as e:
            print(f"Error occured during export: {e}")


    def export_results_to_excel_file(self, file_name):
        print(f"Exporting results to {file_name}...")
        if not self.result:
            print("No results to export. Ensure the screening process was completed successfully.")
            return
        
        try:
            columns = ['Ticker', 'Price', '52-week low', '52-week high', 'Sector', 'Market Cap', 'Current Ratio', 'LTDebtToWC', 'Dividend Record', 'Dividend Yield', 'DGR 10Y', 'P/E Ratio', 'Price-to-book ratio', "Graham's price-to-book ratio"]
            excel = CreateExcelFile.ExcelFile(file_name, columns)

            for ticker, value in self.result.items():
                if value:
                    stock = Stock(ticker)
                    data = self.stock_data(stock)
                    excel.add_stocks(data)

            excel.save()
        except Exception as e:
            print(f"Error occured during export: {e}")
            

    def stock_data(self,ticker: Stock):
        data = {}
        data['Price'] = ticker.yf.info['currentPrice']
        data['52-week low'] = ticker.yf.info['fiftyTwoWeekLow']
        data['52-week high'] = ticker.yf.info['fiftyTwoWeekHigh']
        data["Sector"] = ticker.yf.info['sector']
        data['Market Cap'] = f"{ticker.get_market_cap()/BILLION_DIVISION:.2f}B"
        data['Current Ratio'] = f"{ticker.get_current_ratio():.2f}"
        data['LTDebtToWC'] = f"{ticker.calculate_LTDebt_to_WC():.2f}"
        data['Dividend Record'] = ticker.get_dividend_record_from_excel()
        data["Dividend Yield"] = f"{ticker.yf.info['dividendYield'] * 100}%:.2f"
        data["DGR 10Y"] = f"{ticker.get_DGR_10Y_from_excel()}:.2f"
        data['P/E Ratio'] = f"{ticker.compute_PE_ratio():.2f}"
        data['Price-to-book ratio'] = f"{ticker.compute_price_to_book_ratio():.2f}"
        data["Graham's price-to-book ratio"] = f"{ticker.compute_price_to_book_ratio_graham():.2f}"
        # date['Earnings Stability'] = ticker.check_earnings_stability()
        # date['Earnings Growth'] = ticker.earnings_growth_last_10_years()
        return data