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
            print(f"Error occured during screening: {e}")
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
    def dividend_record_points(self, stock: Stock):
        years_of_increasing_dividens = stock.get_dividend_record_from_excel()
        if years_of_increasing_dividens > 15:
            return 3
        elif 10 <= years_of_increasing_dividens <= 15:
            return 2
        elif years_of_increasing_dividens < 10:
            return 1
        else:
            return 0
        
    # Dividend Yield points
    def dividend_yield_points(self, stock: Stock):
        sp500 = yf.Ticker("SPY")
        sp500_dividend_yield = sp500.info['yield'] * 100
        stock_dividend_yield = stock.get_dividend_yield() * 100
        if stock_dividend_yield > 2.5 * sp500_dividend_yield:
            return 3
        elif sp500_dividend_yield <= stock_dividend_yield <= 2.5 * sp500_dividend_yield:
            return 2
        elif stock_dividend_yield < sp500_dividend_yield:
            return 1
        else:
            return 0
        
    
    # Dividend Growth Rate points
    def DGR_points(self, stock: Stock):
        DGR_1Y = stock.get_DGR_1Y_from_excel()
        stock_dividend_yield = stock.get_dividend_yield() * 100

        # Low dividend yield
        if stock_dividend_yield < 2:
            if DGR_1Y > 13:
                return 3
            elif 9 <= DGR_1Y <= 13:
                return 2
            elif 5 <= DGR_1Y < 9:
                return 1
            else:
                return 0
        
        # Medium dividend yield
        if 2 <= stock_dividend_yield <= 4:
            if DGR_1Y > 10:
                return 3
            elif 5 <= DGR_1Y <= 10:
                return 2
            elif 2 <= DGR_1Y < 5:
                return 1
            else:
                return 0
        
        # High dividend yield
        if stock_dividend_yield > 4:
            if DGR_1Y > 7:
                return 3
            elif 2 <= DGR_1Y <= 7:
                return 2
            elif 1 <= DGR_1Y < 2:
                return 1
            else:
                return 0
            
    # EPS and Earnings Payout Ratio points
    def Earnings_Payout_Ratio_points(self, stock: Stock):
        earnings_payout_ratio = stock.yf.info["payoutRatio"]
        if stock.yf.info['sector'] == "Real Estate":
            if earnings_payout_ratio < 0.8:
                return 3
            elif 0.8 <= earnings_payout_ratio <= 0.9:
                return 2
            elif earnings_payout_ratio > 0.9:
                return 1
        else:
            if earnings_payout_ratio < 0.4:
                return 3
            elif 0.4 <= earnings_payout_ratio <= 0.6:
                return 2
            elif earnings_payout_ratio > 0.6:
                return 1
            
    # FCF Payout Ratio points
    def FCF_Payout_Ratio(self, stock: Stock):
        try:
            free_cash_flow = stock.yf.cashflow.loc['Free Cash Flow'].iloc[0]
            dividens_paid = abs(stock.yf.cashflow.loc['Cash Dividends Paid'].iloc[0])
            if free_cash_flow == 0:
                return 0
            return dividens_paid / free_cash_flow
        except Exception as e:
            print(f"Error calculating FCF Payout Ratio for {stock.ticker}: {e}")
            return 0  # Ensure a return value even in case of failure
    
    def FCF_Payout_Ratio_points(self, stock: Stock):
        FCF_payout_ratio = self.FCF_Payout_Ratio(stock)
        if stock.yf.info['sector'] == "Real Estate":
            if FCF_payout_ratio < 0.8:
                return 3
            elif 0.8 <= FCF_payout_ratio <= 0.9:
                return 2
            elif FCF_payout_ratio > 0.9:
                return 1
        else:
            if FCF_payout_ratio < 0.5:
                return 3
            elif 0.5 <= FCF_payout_ratio <= 0.7:
                return 2
            elif FCF_payout_ratio > 0.7:
                return 1
            
    # Debt to Total Capital points
    def Debt_to_Total_Capital_Ratio(self, stock: Stock):
        balance_sheet = stock.yf.balance_sheet
        total_debt = float(balance_sheet.loc['Total Debt'].iloc[0])
        stockholders_equity = float(balance_sheet.loc['Stockholders Equity'].iloc[0])
        return float(total_debt / (total_debt + stockholders_equity))

    def Debt_to_Total_Capital_points(self, stock: Stock):
        debt_to_capital_ratio = self.Debt_to_Total_Capital_Ratio(stock)
        if debt_to_capital_ratio < 30:
            return 3
        elif 30 <= debt_to_capital_ratio < 60:
            return 2
        elif 60 <= debt_to_capital_ratio <= 80:
            return 1
        
    # ROE points
    def return_on_equity(self, stock: Stock):
        return float(stock.yf.info['returnOnEquity'] * 100)
    
    def return_on_equity_points(self, stock: Stock):
        roe = self.return_on_equity(stock)
        if roe > 25:
            return 3
        elif 10 <= roe <= 25:
            return 2
        elif 5 <= roe < 10:
            return 1
        
    # Operating Income Margin points
    def operating_income_margin(self, stock: Stock):
        return float(stock.yf.info['operatingMargins'] * 100)
    
    def operating_income_margin_points(self, stock: Stock):
        operating_income_margin = self.operating_income_margin(stock)
        if operating_income_margin > 18:
            return 3
        elif 11 <= operating_income_margin <= 18:
            return 2
        elif 5 <= operating_income_margin < 11:
            return 1
        
    # Shares outstanding points
    def ordinary_shares_number_trend_analysis(self, stock: Stock):
        balance_sheet = stock.yf.balance_sheet
        df = balance_sheet.loc["Ordinary Shares Number"].dropna().tolist()

        if len(df) > 2:
            cnt = 0
            for i in range(len(df)-1):
                if df[i] > df[i+1]:
                    return "increase"
                elif df[i] < df[i+1]:
                    cnt += 1
            if cnt == len(df)-1:
                return "consistent decrease"
            else:
                return "chaotic or 0 decrease"

    
    def ordinary_shares_number_points(self, stock: Stock):
        shares_outstanding_trend = self.ordinary_shares_number_trend_analysis(stock)
        if shares_outstanding_trend == "consistent decrease":
            return 3
        elif shares_outstanding_trend == "chaotic or 0 decrease":
            return 2
        elif shares_outstanding_trend == "increase":
            return 1
        else:
            return 0
        
    # Give points to each stock
    def give_points(self, stock: Stock):
        points = 0
        points += self.dividend_record_points(stock)
        points += self.dividend_yield_points(stock)
        points += self.DGR_points(stock)
        points += self.Earnings_Payout_Ratio_points(stock)
        points += self.FCF_Payout_Ratio_points(stock)
        points += self.Debt_to_Total_Capital_points(stock)
        points += self.return_on_equity_points(stock)
        points += self.operating_income_margin_points(stock)
        points += self.ordinary_shares_number_points(stock)
        return points
    

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
            columns = ['Ticker', 'Price', '52-week low', '52-week high', 'Sector', 'Market Cap', 
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
            data['Price'] = f"${ticker.yf.info['currentPrice']}"
            data['52-week low'] = f"${ticker.yf.info['fiftyTwoWeekLow']:.2f}"
            data['52-week high'] = f"${ticker.yf.info['fiftyTwoWeekHigh']:.2f}"
            data["Sector"] = ticker.yf.info['sector']
            data['Market Cap'] = f"{ticker.get_market_cap()/BILLION_DIVISION:.2f}B"
            data['Current Ratio'] = f"{ticker.get_current_ratio():.2f}"
            data['LTDebtToWC'] = f"{ticker.calculate_LTDebt_to_WC():.2f}"
            data["Earnings Stability"] = ticker.check_earnings_stability()
            data["Earnings Growth Over the past 10 Years"] = f"{ticker.earnings_growth_last_10_years():.2f}"
            data['Dividend Record'] = ticker.get_dividend_record_from_excel()
            data["Dividend Yield"] = f"{ticker.yf.info['dividendYield'] * 100:.2f}%"
            data["DGR 1Y"] = f"{ticker.get_DGR_1Y_from_excel()}%"
            data["DGR 10Y"] = f"{ticker.get_DGR_10Y_from_excel()}%"
            data["ROCE"] = f"{ticker.compute_ROCE()*100:.2f}%"
            data["Operating Income Margin"] = f"{self.operating_income_margin(ticker):.2f}%"
            data["Debt to Total Capital"] = f"{self.Debt_to_Total_Capital_Ratio(ticker):.2f}"
            data["ROE"] = f"{self.return_on_equity(ticker):.2f}%"
            data["Earnings Payout Ratio"] = f"{ticker.yf.info['payoutRatio'] * 100:.2f}%"
            data["FCF Payout Ratio"] = f"{self.FCF_Payout_Ratio(ticker) * 100:.2f}%"
            data["Ordinary Share Number Trend"] = self.ordinary_shares_number_trend_analysis(ticker)
            data['P/E Ratio'] = f"{ticker.compute_PE_ratio():.2f}"
            data['Price-to-book ratio'] = f"{ticker.compute_price_to_book_ratio():.2f}"
            data["Graham's price-to-book ratio"] = f"{ticker.compute_price_to_book_ratio_graham():.2f}"
            data["Points"] = self.give_points(ticker)
        except Exception as e:
            print(f"Error getting data for {ticker.ticker}: {e}")
        return data