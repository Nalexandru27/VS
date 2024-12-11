from concurrent.futures import ThreadPoolExecutor, as_completed
import EvalutateStock as es
import numpy as np
from Stock import *
import pandas as pd
import CreateExcelFile
import time

class StockScreener:
    def __init__(self):
        self.result = {}

    # TEST 1
    # Market Capitalization > 2 billion
    def check_market_cap(self, stock: Stock):
        market_cap = stock.get_market_cap()
        return float(market_cap) >= MIN_MARKET_CAP
    
    # TEST 2.1
    # Current Ratio >= 2
    def check_current_ratio(self, stock: Stock):
        current_ratio = stock.get_current_ratio()
        return float(current_ratio) >= MIN_CURRENT_RATIO

    # TEST 2.2
    # Long-Term Debt to Working Capital Ratio <= 1
    def check_LTDebt_To_WC(self, stock: Stock):
        LTDebtToWC = stock.calculate_LTDebt_to_WC()
        return 0 < LTDebtToWC and LTDebtToWC <= MAX_LONG_TERM_DEBT_TO_WORKING_CAPITAL_RATIO

    # TEST 3
    # Earnings stability - Positive net income for the past 10 years & using Alpha Vantage
    def check_earnings_stability(self, stock: Stock):
        annual_report = stock.get_income_stmt_from_alphavantage()
        i = 0
        for report in annual_report:
            try:
                if i >= 10:
                    break
                if float(report['netIncome']) < 0:
                    return False
                i += 1
            except KeyError:
                print("Error: 'netIncome' or 'fiscalDateEnding' missing key in annual report")
                continue
        return True
    
    # TEST 4
    # Check if the stock has increased its dividend for more than 10 years in a row
    def check_dividend_record(self, stock: Stock):
        return stock.count_consecutive_years_of_dividend_increase() >= INCREASED_DIVIDEND_RECORD

    # TEST 5
    # Check if the last 3 years earnings did grow more than 33% vs the earnings from the 8,9,10 year from the past
    def check_earnings_growth(self, stock: Stock):
        earnings_growth = stock.earnings_growth_last_10_years()
        if earnings_growth < EARNINGS_GROWTH_THRESHOLD:
            return False
        return True
    
    # TEST 6
    # Check if the stock has a P/E ratio between 0 and 15
    def check_PE_ratio(self, stock: Stock):
        pe_ratio = stock.compute_PE_ratio()
        return 0 < pe_ratio and pe_ratio <= PE_RATIO_THRESHOLD
    
    # TEST 7
    # Check if the stock has a price to book ratio between 0 and 1.5
    def check_price_to_book_ratio(self, stock: Stock):
        price_to_book_ratio = stock.compute_price_to_book_ratio()
        return 0 < price_to_book_ratio and price_to_book_ratio <= PRICE_TO_BOOK_RATIO 

    # TEST 8
    # Check if the stock has a price to book ratio between 0 and 22.5 using Graham's formula
    def check_price_to_book_ratio_graham(self, stock: Stock):
        price_to_book_ratio_graham = stock.compute_price_to_book_ratio_graham()
        return 0 < price_to_book_ratio_graham and price_to_book_ratio_graham <= PRICE_TO_BOOK_RATIO_GRAHAM

    # Implement testing criterias
    def validate_criterias(self, stock: Stock):
        # Check Current Ratio
        if stock.yf.info["sector"] != "Utilities":
            current_ratio = stock.get_current_ratio()
            if current_ratio == 0:
                print(f"{stock.ticker} has no data available for the current ratio. Test skipped")
            elif not self.check_current_ratio(stock):
                print(f"-->{stock.ticker} failed the test 'Current Ratio'")
                return False
        else:
            print(f"{stock.ticker} is a utility company. Current ratio test skipped")

        # Check Long-Term Debt to Working Capital
        long_term_debt_to_workin_capital = stock.calculate_LTDebt_to_WC()
        if long_term_debt_to_workin_capital == 0:
            print(f"{stock.ticker} has no data available for the long-term debt to working capital ratio. Test skipped")
        elif not self.check_LTDebt_To_WC(stock):
            print(f"-->{stock.ticker} failed the test 'Long-Term Debt to Working Capital'")
            return False

        # Check Market Cap
        market_cap = stock.get_market_cap()
        if market_cap == 0:
            print(f"{stock.ticker} has no data available for the market capitalization. Test skipped")
        elif not self.check_market_cap(stock):
            print(f"-->{stock.ticker} failed the test 'Market Cap'")
            return False

        # Check P/E Ratio
        pe_ratio = stock.compute_PE_ratio()
        if pe_ratio == 0:
            print(f"{stock.ticker} has no data available for the P/E ratio. Test skipped")
        elif not self.check_PE_ratio(stock):
            print(f"-->{stock.ticker} failed the test 'P/E Ratio'")
            return False

        # Check Price_To_Book_Ratio normal and using Graham's formula
        price_to_book_ratio = stock.compute_price_to_book_ratio()
        price_to_book_ratio_graham = stock.compute_price_to_book_ratio_graham()
        if price_to_book_ratio == 0 and price_to_book_ratio_graham == 0:
            print(f"{stock.ticker} has no data available for the price-to-book ratio (normal and graham). Test skipped")
        elif not self.check_price_to_book_ratio(stock) and not self.check_price_to_book_ratio_graham(stock):
            print(f"-->{stock.ticker} failed the test 'Price-to-book ratio' and 'Graham's price-to-book ratio'")
            return False
        
        # Check Dividend Record
        # if not stock.check_dividend_record():
        #     print(f"-->{stock.ticker} failed the test 'Dividend Record'")
        #     return False

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
                        'Current Ratio', 'LTDebtToWC', 'Earnings Stability', 'Earnings Growth over past 10Y',
                        'Dividend Record', 'Dividend Yield', 'DGR 1Y', 'DGR 3Y', 'DGR 10Y', "ROCE", 'Operating Income Margin',
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
                        time.sleep(10)
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
        evaluator = es.evaluateStock(ticker, FILE_PATH_1)
        income_statement = ticker.get_income_statement
        balance_sheet = ticker.get_balance_sheet
        cash_flows = ticker.get_cashflow_data
        
        try:
            data['Ticker'] = ticker.ticker
            data["Sector"] = ticker.yf.info['sector']
            data['Market Cap'] = f"{ticker.get_market_cap()/BILLION_DIVISION:.2f}B"
            data['Current Ratio'] = f"{ticker.get_current_ratio():.2f}"
            data['LTDebtToWC'] = f"{ticker.calculate_LTDebt_to_WC():.2f}"
            data['Earnings Stability'] = self.check_earnings_stability(ticker)
            data['Earnings Growth over past 10Y'] = ticker.earnings_growth_last_10_years()
            data['Dividend Record'] = ticker.get_dividend_record_from_excel(FILE_PATH_1)
            data["Dividend Yield"] = f"{ticker.yf.info['dividendYield'] * 100:.2f}%"
            data["DGR 3Y"] = f"{ticker.get_DGR_3Y_from_excel(FILE_PATH_1)}%"
            data["DGR 5Y"] = f"{ticker.get_DGR_5Y_from_excel(FILE_PATH_1)}%"
            data["DGR 10Y"] = f"{ticker.get_DGR_10Y_from_excel(FILE_PATH_1)}%"
            data["ROCE"] = f"{ticker.compute_ROCE() * 100:.2f}%"
            data["Operating Income Margin"] = f"{ticker.operating_income_margin():.2f}%"
            data["Debt to Total Capital"] = f"{ticker.Debt_to_Total_Capital_Ratio():.2f}"
            data["ROE"] = f"{ticker.return_on_equity():.2f}%"
            data["Earnings Payout Ratio"] = f"{ticker.yf.info['payoutRatio'] * 100:.2f}%"
            data["FCF Payout Ratio"] = f"{ticker.FCF_Payout_Ratio() * 100:.2f}%"
            data["Ordinary Share Number Trend"] = ticker.ordinary_shares_number_trend_analysis()
            data['P/E Ratio'] = f"{ticker.compute_PE_ratio():.2f}"
            data['Price-to-book ratio'] = f"{ticker.compute_price_to_book_ratio():.2f}"
            data["Graham's price-to-book ratio"] = f"{ticker.compute_price_to_book_ratio_graham():.2f}"
            data["Points"] = evaluator.give_points()
        except Exception as e:
            print(f"Error getting data for {ticker.ticker}: {e}")
        return data