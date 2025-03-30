from concurrent.futures import ThreadPoolExecutor, as_completed
import stock.EvalutateStock as es
from stock.Stock import *
import utils.CreateExcelFile as CreateExcelFile
import database.DatabaseCRUD as db
from utils.Constants import FILTERED_DIVIDEND_COMPANY_FILE_PATH
from database.DatabaseConnection import db_connection

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
        LTDebtToWC = stock.get_LTDebt_to_WC()
        return 0 < LTDebtToWC and LTDebtToWC <= MAX_LONG_TERM_DEBT_TO_WORKING_CAPITAL_RATIO

    # TEST 3
    # Earnings stability - Positive net income for the past 10 years
    def check_earnings_stability(self, stock: Stock):
        return stock.earnings_stability()
    
    # TEST 4
    # Check if the stock has increased its dividend for more than 10 years in a row
    def check_dividend_record(self, stock: Stock):
        return stock.get_dividend_record_from_excel(FILTERED_DIVIDEND_COMPANY_FILE_PATH) >= INCREASED_DIVIDEND_RECORD

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
        # Check Long-Term Debt to Working Capital
        long_term_debt_to_workin_capital = stock.get_LTDebt_to_WC()
        if long_term_debt_to_workin_capital == 0:
            print(f"{stock.ticker} has no data available for the long-term debt to working capital ratio. Test skipped")
        elif self.check_LTDebt_To_WC(stock) == False:
            print(f"-->{stock.ticker} failed the test 'Long-Term Debt to Working Capital'")
            return False

        # Check Current Ratio
        if stock.get_sector() != "Utilities":
            current_ratio = stock.get_current_ratio()
            if current_ratio == 0:
                print(f"{stock.ticker} has no data available for the current ratio. Test skipped")
            elif self.check_current_ratio(stock) == False:
                print(f"-->{stock.ticker} failed the test 'Current Ratio'")
                return False
        else:
            print(f"{stock.ticker} is a utility company. Current ratio test skipped")

        # Check Market Cap
        market_cap = stock.get_market_cap()
        if market_cap == 0:
            print(f"{stock.ticker} has no data available for the market capitalization. Test skipped")
        elif self.check_market_cap(stock) == False:
            print(f"-->{stock.ticker} failed the test 'Market Cap'")
            return False

        # Check P/E Ratio
        pe_ratio = stock.compute_PE_ratio()
        if pe_ratio == 0:
            print(f"{stock.ticker} has no data available for the P/E ratio. Test skipped")
        elif self.check_PE_ratio(stock) == False:
            print(f"-->{stock.ticker} failed the test 'P/E Ratio'")
            return False

        # Check Price_To_Book_Ratio normal and using Graham's formula
        price_to_book_ratio = stock.compute_price_to_book_ratio()
        price_to_book_ratio_graham = stock.compute_price_to_book_ratio_graham()
        if price_to_book_ratio == 0 and price_to_book_ratio_graham == 0:
            print(f"{stock.ticker} has no data available for the price-to-book ratio (normal and graham). Test skipped")
        elif self.check_price_to_book_ratio(stock) == False and self.check_price_to_book_ratio_graham(stock) == False:
            print(f"-->{stock.ticker} failed the test 'Price-to-book ratio' and 'Graham's price-to-book ratio'")
            return False
        
        # # Check Dividend Record
        if self.check_dividend_record(stock) == False:
            print(f"-->{stock.ticker} failed the test 'Dividend Record'")
            return False

        # Check Earnings Stability
        earnings_stability = self.check_earnings_stability(stock)
        if earnings_stability == 0:
            print(f"{stock.ticker} has no data available to check the earnings stability. Test skipped")
        elif self.check_earnings_stability(stock) == False:
            print(f"-->{stock.ticker} failed the test 'Earnings Stability'")
            return False

        # Check Earnings Growth
        if self.check_earnings_growth(stock) == False:
            print(f"-->{stock.ticker} failed the test 'Earnings Growth'")
            return False

        # All tests passed
        print(f"{stock.ticker} passed all tests")
        return True

    # Screen a list of stocks in parallel with multi threading
    # def screen_stocks(self, tickers):
    #     results = {}
        
    #     def process_ticker(ticker):
    #         try:
    #             print(f"Screening {ticker}...")
    #             stock = Stock(ticker)

    #             if stock.db_crud.select_company(ticker) is None:
    #                 print(f"No data found for ticker '{ticker}'. Skipping.")
    #                 return (ticker, False)

    #             result = self.validate_criterias(stock)
    #             return (ticker, result)
    #         except Exception as e:
    #             print(f"Error screening {ticker}: {e}")
    #             return (ticker, False)
            
    #     max_workers = min(10, len(tickers))
        
    #     with ThreadPoolExecutor(max_workers=max_workers) as executor:
    #         futures = [executor.submit(process_ticker, ticker) for ticker in tickers]
    #         for future in as_completed(futures):
    #             try:
    #                 ticker, result = future.result()
    #                 results[ticker] = result
    #             except Exception as e:
    #                 print(f"Error processing ticker result: {e}")
        
    #     self.result = results
    #     print("\nScreening done.\n")
    #     return results

    # Screen a list of stocks in sequence without multi threading
    def screen_stocks(self, tickers):
        results = {}
        for ticker in tickers:
            try:
                print(f"Screening {ticker}...")
                stock = Stock(ticker)
                company_id = stock.db_crud.select_company(ticker)
                print(f"Company ID for {ticker}: {company_id}")
                
                if company_id is None:
                    print(f"No data found for ticker '{ticker}'. Skipping.")
                    results[ticker] = False
                    continue

                result = self.validate_criterias(stock)
                results[ticker] = result
            except Exception as e:
                print(f"Error screening {ticker}: {e}")
                results[ticker] = False
        
        self.result = results
        print("\nScreening done.\n")
        return results

    # Export results to an Excel file
    def export_results_to_excel_file(self, file_name):
        print(f"Exporting results to {file_name}...")
        if not self.result:
            print("No results to export. Ensure the screening process was completed successfully.")
            return
        try:
            columns = ['Ticker', 'Sector',  'Market Cap',
                        'Current Ratio', 'LTDebtToWC', 'Earnings Stability', 'Earnings Growth 10Y',
                        'Dividend Record', 'Dividend Yield', 'DGR 3Y', 'DGR 5Y', 'DGR 10Y', 
                        'Div/share', 'EPS', 'FCF/share', 'OpCF/share', 'Earnings Payout Ratio', 'FCF Payout Ratio', 'OpCF Payout Ratio',
                        'Debt/Capital', 'Op Income Margin', 'ROCE', 'ROE', 'Ordinary Share Number Trend', 'P/E Ratio', 'Price-to-book ratio', 'Graham\'s price-to-book ratio',
                        'Points']         
            excel = CreateExcelFile.ExcelFile(file_name, columns)

            stock_data_list = []

            # Process each ticker in parallel with multi threading
            # def process_ticker(ticker):
            #     if self.result[ticker]:
            #         try:
            #             print(f"Processing {ticker}...")
            #             stock = Stock(ticker)
            #             data = self.stock_data(stock)
            #             if data is not None:
            #                 print(f"Data for {ticker} processed successfully.")
            #                 return data
            #             else:
            #                 print(f"No data for {ticker}.")
            #                 return None
            #         except Exception as e:
            #             print(f"Error processing {ticker}: {e}")
            #             return None
            
            # with ThreadPoolExecutor(max_workers=5) as executor:
            #     future_to_ticker = {executor.submit(process_ticker, ticker): ticker
            #                         for ticker in self.result if self.result[ticker]} 
                
            #     for future in as_completed(future_to_ticker):
            #         data = future.result()
            #         if data is not None:
            #             stock_data_list.append(data)

            # Process each ticker in sequence without multi threading
            for ticker in self.result:
                if self.result[ticker]:
                    try:
                        print(f"Processing {ticker}...")
                        stock = Stock(ticker)
                        data = self.stock_data(stock)
                        if data is not None:
                            print(f"Data for {ticker} processed successfully.")
                            stock_data_list.append(data)
                        else:
                            print(f"No data for {ticker}.")
                    except Exception as e:
                        print(f"Error processing {ticker}: {e}")

            for stock_data in stock_data_list:
                excel.add_stocks(stock_data)

            excel.save()
        except Exception as e:
            print(f"Error occured during export: {e}")

    
    def stock_data(self,ticker: Stock):
        data = {}
        evaluator = es.evaluateStock(ticker, FILTERED_DIVIDEND_COMPANY_FILE_PATH)
        try:
            data['Ticker'] = ticker.ticker
            sector = ticker.db_crud.select_company_sector(ticker.ticker)
            data["Sector"] = sector
            data['Market Cap'] = f"{ticker.get_market_cap()/BILLION_DIVISION:.2f}B"
            data['Current Ratio'] = f"{ticker.get_current_ratio():.2f}"
            data['LTDebtToWC'] = f"{ticker.get_LTDebt_to_WC():.2f}"
            data['Earnings Stability'] = self.check_earnings_stability(ticker)
            data['Earnings Growth 10Y'] = f"{ticker.earnings_growth_last_10_years():.2f}"
            data['Dividend Record'] = ticker.get_dividend_record_from_excel(FILTERED_DIVIDEND_COMPANY_FILE_PATH)
            data["Dividend Yield"] = f"{ticker.get_dividend_yield() * 100:.2f}%"
            data["DGR 3Y"] = f"{ticker.get_DGR_3Y_from_excel(FILTERED_DIVIDEND_COMPANY_FILE_PATH)}%"
            data["DGR 5Y"] = f"{ticker.get_DGR_5Y_from_excel(FILTERED_DIVIDEND_COMPANY_FILE_PATH)}%"
            data["DGR 10Y"] = f"{ticker.get_DGR_10Y_from_excel(FILTERED_DIVIDEND_COMPANY_FILE_PATH)}%"
            data["Div/share"] = f"{ticker.dividends_per_share():.2f}"
            data["EPS"] = f"{ticker.get_EPS():.2f}"
            data["FCF/share"] = f"{ticker.get_fcf_per_share():.2f}"
            data["OpCF/share"] = f"{ticker.get_operating_cash_flow_per_share():.2f}"
            data["Earnings Payout Ratio"] = f"{ticker.earnings_payout_ratio() * 100:.2f}%"
            data["FCF Payout Ratio"] = f"{ticker.FCF_Payout_Ratio() * 100:.2f}%"
            data["OpCF Payout Ratio"] = f"{ticker.get_operating_cash_flow_payout_ratio() * 100:.2f}%"
            data["Debt/Capital"] = f"{ticker.Debt_to_Total_Capital_Ratio() * 100:.2f}%"
            data["Op Income Margin"] = f"{ticker.operating_income_margin() * 100:.2f}%"
            data["ROCE"] = f"{ticker.compute_ROCE() * 100:.2f}%"
            data["ROE"] = f"{ticker.return_on_equity() * 100:.2f}%"
            data["Ordinary Share Number Trend"] = ticker.ordinary_shares_number_trend_analysis()
            data['P/E Ratio'] = f"{ticker.compute_PE_ratio():.2f}"
            data['Price-to-book ratio'] = f"{ticker.compute_price_to_book_ratio():.2f}"
            data["Graham's price-to-book ratio"] = f"{ticker.compute_price_to_book_ratio_graham():.2f}"
            data["Points"] = evaluator.give_points()
        except Exception as e:
            print(f"Error getting data for {ticker.ticker}: {e}")
        return data