import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PriceEstimators.PriceEstimationEarnings import PERatioEstimator
from PriceEstimators.PriceEstimationEBIT import PEBITRatioEstimator
from PriceEstimators.PriceEstimationOpCF import PriceOpCFRatioEstimator
from PriceEstimators.PriceEstimationFCF import PriceFCFRatioEstimator
from PriceEstimators.PriceEstimationDividend import PriceDividendRatioEstimator
from stock.Stock import Stock
from utils.SafeDivide import safe_divide
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def get_price_estimation(ticker):
    price_pe = None
    price_ebit = None
    price_op_cf = None
    price_fcf = None
    price_dividend = None

    try:
        pe_ratio = PERatioEstimator(Stock(ticker))
        price_pe = pe_ratio.get_pe_ratio_estimation(2013, 2023)
        # print(f"The price estimation using P/E ratio: {price_pe:.2f}$")
    except Exception as e:
        print("Error occured when computing price_pe", e)

    try:
        ebit_price = PEBITRatioEstimator(Stock(ticker))
        price_ebit = ebit_price.get_pebit_ratio_estimation(2013, 2023)
        # print(f"The price estimation using P/EBIT ratio: {price_ebit:.2f}$")
    except Exception as e:
        print("Error occured when computing price_ebit", e)

    try:
        op_cf_price = PriceOpCFRatioEstimator(Stock(ticker))
        price_op_cf = op_cf_price.get_priceOpCF_ratio_estimation(2013, 2023)
        # print(f"The price estimation using P/OpCF ratio: {price_op_cf:.2f}$")
    except Exception as e:
        print("Error occured when computing price_op_cf", e)

    try:
        fcf_price_estimator = PriceFCFRatioEstimator(Stock(ticker))
        price_fcf = fcf_price_estimator.get_priceFCF_ratio_estimation(2013, 2023)
        # print(f"The price estimation using PEBIT ratio: {price_fcf:.2f}$")
    except Exception as e:
        print("Error occured when computing price_fcf", e)

    try:
        dividend_price_estimator = PriceDividendRatioEstimator(Stock(ticker))
        price_dividend = dividend_price_estimator.get_priceDividend_ratio_estimation(2013, 2023)
        # print(f"The price estimation using P/Dividend ratio: {price_dividend:.2f}$")
    except Exception as e:
        print("Error occured when computing price_dividend", e)

    values = [val for val in [price_pe, price_ebit, price_op_cf, price_fcf, price_dividend] if val is not None]
    
    if not values:
        return 0
    
    avg_price = safe_divide(sum(values), len(values))

    return avg_price