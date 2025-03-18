import pandas as pd

def handling_missing_prices_history():
    df = pd.read_csv("outData/cleand_PriceHistory.csv", index_col=0)
    available_date_percentage = (1 - df.isnull().mean()) * 100

    valid_companies = available_date_percentage[available_date_percentage >= 75].index
    df_filtered = df[valid_companies]

    df_filled = df_filtered.interpolate(method='linear', limit=5)

    still_missing = df_filled.isnull()

    df_ffill = df_filled.ffill()
    df_bfill = df_filled.bfill()

    df_filled[still_missing] = (df_ffill[still_missing] + df_bfill[still_missing]) / 2

    if df_filled.isnull().sum().sum() > 0 :
        df_filled = df_filled.fillna(df_filled.ewm(span=30).mean())

    df_filled = df_filled.fillna(df_filled.mean())

    df_filled.to_csv("outData/filled_PriceHistory.csv")