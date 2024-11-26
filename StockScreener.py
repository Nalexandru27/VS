from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from Stock import *
import pandas as pd
import CreateExcelFile

class StockScreener:
    def __init__(self):
        self.result = {}

    def validate_criterias(self, stock: Stock):
        try:
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

            # Check Market Cap
            if not stock.check_market_cap():
                print(f"-->{stock.ticker} failed the test 'MarketCap'")
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
            print(f"Error occured during screening for company {stock.ticker}: {e}")
            return False
    

    # Export results to a text file
    # def export_results_to_text_file(self, file_name):
    #     print(f"Exporting results to {file_name}...")
    #     if not self.result:
    #         print("No results to export. Ensure the screening process was completed successfully.")
    #         return
        
    #     # Process each ticker in parallel
    #     def process_ticker(ticker):
    #         try:
    #             if self.result[ticker]:
    #                 stock = Stock(ticker)
    #                 data = self.stock_data(stock)
    #                 result = f"{ticker} passed all tests\n"
    #                 result += "\n".join([f"{key}: {value}" for key, value in data.items()])
    #                 result += "\n----------------------\n"
    #                 return result
    #             return ""
    #         except Exception as e:
    #             return f"Error processing {ticker}: {e}\n"

    #     try:
    #         with ThreadPoolExecutor() as executor:
    #             futures = [executor.submit(process_ticker, ticker) for ticker in self.result]
    #             results = [future.result() for future in futures]

    #         with open(file_name, 'w') as file:
    #             file.writelines(results)

    #         print(f"Results exported to {file_name}")
    #     except Exception as e:
    #         print(f"Error occured during export: {e}")

    # Dividend Record points
    
    

    # Screen a list of stocks in parallel
    def screen_stocks(self, tickers):
        def process_ticker(ticker):
            print(f"Screening {ticker}...")
            stock = Stock(ticker)
            self.result[ticker] = self.validate_criterias(stock)
        
        with ThreadPoolExecutor() as executor:
            executor.map(process_ticker, tickers)

        print("\nScreening done.\n")


    # Inspect the results of the screening process and print the stocks that passed all tests in the terminal
    def inspect_results_of_screening(self):
        for ticker, value in self.result.items():
            if value:
                print(f'{ticker} passed all tests')
                stock = Stock(ticker)
                stock.print_results()
            else:
                print(f"{ticker} did not pass all the test")
                print("\n")


    # Export results to an Excel file
    def export_results_to_excel_file(self, file_name):
        print(f"Exporting results to {file_name}...")
        if not self.result:
            print("No results to export. Ensure the screening process was completed successfully.")
            return
        
        try:
            columns = ['Ticker', 'Sector', 'Market Cap', 
                        'Current Ratio', 'LTDebtToWC', 'Earnings Stability', 'Earnings Growth Over the past 10 Years',
                        'Dividend Record', 'Dividend Yield', 'DGR 1Y', 'DGR 10Y', "ROCE", 'Operating Income Margin',
                        'Debt to Total Capital', 'ROE', 'Earnings Payout Ratio', 'FCF Payout Ratio', 'Ordinary Share Number Trend',
                        'P/E Ratio', 'Price-to-book ratio', "Graham's price-to-book ratio", 'Points']         
            excel = CreateExcelFile.ExcelFile(file_name, columns)

            stock_data_list = []

            # Process each ticker in parallel
            def process_ticker(ticker):
                if self.result[ticker]:
                    try:
                        print(f"Processing {ticker}...")
                        stock = Stock(ticker)
                        data = self.stock_data(stock)
                        if data is not None:
                            print(f"Data for {ticker} processed successfully.")
                            return data
                        else:
                            print(f"No data for {ticker}.")
                            return None
                    except Exception as e:
                        print(f"Error processing {ticker}: {e}")
                        return None
            
            with ThreadPoolExecutor() as executor:
                future_to_ticker = {executor.submit(process_ticker, ticker): ticker
                                    for ticker in self.result if self.result[ticker]} 
                
                for future in as_completed(future_to_ticker):
                    data = future.result()
                    if data is not None:
                        stock_data_list.append(data)

            for stock_data in stock_data_list:
                excel.add_stocks(stock_data)

            excel.save()
        except Exception as e:
            print(f"Error occured during export: {e}")


    def stock_data(self,ticker: Stock):
        data = {}
        try:
            data['Ticker'] = ticker.ticker
            data["Sector"] = ticker.yf.info['sector']
            data['Market Cap'] = f"{ticker.get_market_cap()/BILLION_DIVISION:.2f}B"
            data['Current Ratio'] = f"{ticker.get_current_ratio():.2f}"
            data['LTDebtToWC'] = f"{ticker.calculate_LTDebt_to_WC():.2f}"
            data['Dividend Record'] = ticker.get_dividend_record_from_excel()
            data["Dividend Yield"] = f"{ticker.yf.info['dividendYield'] * 100:.2f}%"
            data["DGR 1Y"] = f"{ticker.get_DGR_1Y_from_excel()}%"
            data["DGR 10Y"] = f"{ticker.get_DGR_10Y_from_excel()}%"
            data["ROCE"] = f"{ticker.compute_ROCE() * 100:.2f}%"
            data["Operating Income Margin"] = f"{ticker.operating_income_margin():.2f}%"
            data["Debt to Total Capital"] = f"{ticker.Debt_to_Total_Capital_Ratio():.2f}"
            data["ROE"] = f"{ticker.return_on_equity(ticker):.2f}%"
            data["Earnings Payout Ratio"] = f"{ticker.yf.info['payoutRatio'] * 100:.2f}%"
            data["FCF Payout Ratio"] = f"{ticker.FCF_Payout_Ratio() * 100:.2f}%"
            data["Ordinary Share Number Trend"] = ticker.ordinary_shares_number_trend_analysis()
            data['P/E Ratio'] = f"{ticker.compute_PE_ratio():.2f}"
            data['Price-to-book ratio'] = f"{ticker.compute_price_to_book_ratio():.2f}"
            data["Graham's price-to-book ratio"] = f"{ticker.compute_price_to_book_ratio_graham():.2f}"
            data["Earnings Stability"] = ticker.check_earnings_stability()
            data["Earnings Growth Over the past 10 Years"] = f"{ticker.earnings_growth_last_10_years():.2f}"
            data["Points"] = ticker.give_points(ticker)
        except Exception as e:
            print(f"Error getting data for {ticker.ticker}: {e}")
        return data