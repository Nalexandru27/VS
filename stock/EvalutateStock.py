from stock.Stock import *
from utils.Constants import *
from database.DatabaseCRUD import DatabaseCRUD

class evaluateStock:
    def __init__(self, stock: Stock, filePath):
        self.stock = stock
        self.filePath = filePath

    def dividend_record_points(self):
        years_of_increasing_dividens = self.stock.get_dividend_record_from_excel(self.filePath)
        if years_of_increasing_dividens > 15:
            return 3
        elif 10 <= years_of_increasing_dividens <= 15:
            return 2
        elif years_of_increasing_dividens < 10:
            return 1
        else:
            return 0
        
    # Dividend Yield points
    def dividend_yield_points(self):
        sp500_dividend_yield = 1.27
        stock_dividend_yield = self.stock.get_dividend_yield() * 100
        if stock_dividend_yield > 2.5 * sp500_dividend_yield:
            return 3
        elif sp500_dividend_yield <= stock_dividend_yield <= 2.5 * sp500_dividend_yield:
            return 2
        elif stock_dividend_yield < sp500_dividend_yield:
            return 1
        else:
            return 0
        
    
    # Dividend Growth Rate points
    def DGR_points(self):
        DGR_10Y = self.stock.get_DGR_10Y_from_excel(self.filePath)
        stock_dividend_yield = self.stock.get_dividend_yield() * 100

        # Low dividend yield
        if stock_dividend_yield < 2:
            if DGR_10Y > 13:
                return 3
            elif 9 <= DGR_10Y <= 13:
                return 2
            elif 5 <= DGR_10Y < 9:
                return 1
            else:
                return 0
        
        # Medium dividend yield
        if 2 <= stock_dividend_yield <= 4:
            if DGR_10Y > 10:
                return 3
            elif 5 <= DGR_10Y <= 10:
                return 2
            elif 2 <= DGR_10Y < 5:
                return 1
            else:
                return 0
        
        # High dividend yield
        if stock_dividend_yield > 4:
            if DGR_10Y > 7:
                return 3
            elif 2 <= DGR_10Y <= 7:
                return 2
            elif 1 <= DGR_10Y < 2:
                return 1
            else:
                return 0
            
    # EPS and Earnings Payout Ratio points
    def Earnings_Payout_Ratio_points(self):
        earnings_payout_ratio = self.stock.earnings_payout_ratio()
        sector = self.stock.db_crud.select_company_sector(self.stock.ticker)
        if sector == "Real Estate":
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
        return 0
            
    # FCF Payout Ratio points
    def FCF_Payout_Ratio_points(self):
        FCF_payout_ratio = self.stock.FCF_Payout_Ratio()
        sector = self.stock.db_crud.select_company_sector(self.stock.ticker)
        if sector == "Real Estate":
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
        return 0
            
    # Debt to Total Capital points
    def Debt_to_Total_Capital_points(self):
        debt_to_capital_ratio = self.stock.Debt_to_Total_Capital_Ratio()
        if 0 < debt_to_capital_ratio < 30:
            return 3
        elif 30 <= debt_to_capital_ratio < 60:
            return 2
        elif 60 <= debt_to_capital_ratio <= 80:
            return 1
        else:
            return 0
        
    # ROE points
    def return_on_equity_points(self):
        try:
            roe = self.stock.return_on_equity()
            if roe > 25:
                return 3
            elif 10 <= roe <= 25:
                return 2
            elif 5 <= roe < 10:
                return 1
            else:
                return 0
        except Exception as e:
            print(f"Error: {e}")
            return 0
        
    # Operating Income Margin points    
    def operating_income_margin_points(self):
        operating_income_margin = self.stock.operating_income_margin()
        if operating_income_margin > 18:
            return 3
        elif 11 <= operating_income_margin <= 18:
            return 2
        elif 5 <= operating_income_margin < 11:
            return 1
        else:
            return 0
        
    # Shares outstanding points    
    def ordinary_shares_number_points(self):
        shares_outstanding_trend = self.stock.ordinary_shares_number_trend_analysis()
        if shares_outstanding_trend == "consistent decrease":
            return 3
        elif shares_outstanding_trend == "chaotic or 0 decrease":
            return 2
        elif shares_outstanding_trend == "increase":
            return 1
        else:
            return 0

    # Sum up stock points 
    def give_points(self):
        points = 0
        points += self.dividend_record_points()
        points += self.dividend_yield_points()
        points += self.DGR_points()
        points += self.Earnings_Payout_Ratio_points()
        points += self.FCF_Payout_Ratio_points()
        points += self.Debt_to_Total_Capital_points()
        points += self.return_on_equity_points()
        points += self.operating_income_margin_points()
        points += self.ordinary_shares_number_points()
        return points