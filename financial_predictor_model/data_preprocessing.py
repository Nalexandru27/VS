import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.DatabaseCRUD import DatabaseCRUD
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

db_crud = DatabaseCRUD()

def create_prices_dataframe_of_company(ticker, start_date, end_date):
    prices = db_crud.get_prices(ticker, start_date, end_date)
    df = pd.DataFrame(prices, columns=['Date', 'Close Price'])
    df = df.set_index('Date')
    return df

def add_technical_indicators(df):
    """
    Adaugă indicatori tehnici la dataframe-ul de prețuri
    """
    # Ne asigurăm că avem o coloană 'Close' pentru compatibilitate
    if 'Close Price' in df.columns and 'Close' not in df.columns:
        df['Close'] = df['Close Price']

    # Calculăm medii mobile pe diferite perioade
    df['MA5'] = df['Close'].rolling(window=5).mean() 
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    # Calculăm RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Calculăm volatilitatea (deviația standard în ultimele 20 de zile)
    df['Volatility'] = df['Close'].rolling(window=20).std()

    # Calculăm procentul de schimbare zilnică
    df['Daily_Return'] = df['Close'].pct_change()

    # Eliminăm valorile NaN rezultate din calculele de mai sus
    df = df.dropna()

    return df

def normalize_date(df):
    """
    Normalizează datele pentru a fi utilizate în modelul LSTM.
    Elimină sau înlocuiește valorile problematice precum NaN și inf.
    """

    import numpy as np

    scaler = MinMaxScaler(feature_range=(0, 1))

    # Selectăm coloanele numerice
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    # Înlocuim inf cu NaN
    df[numerical_cols] = df[numerical_cols].replace([np.inf, -np.inf], np.nan)

    # Completăm NaN cu interpolare liniară (sau media ca alternativă)
    df[numerical_cols] = df[numerical_cols].interpolate(method='linear', limit_direction='forward', axis=0)

    # Dacă mai rămân NaN la început sau sfârșit, completăm cu medie
    df[numerical_cols] = df[numerical_cols].fillna(df[numerical_cols].mean())

    # Aplicăm scalarea
    for col in numerical_cols:
        df[col] = scaler.fit_transform(df[[col]])

    return df, scaler

def create_sequences(df, seq_length=60):
    """
    Creează secvențe pentru antrenarea modelului LSTM
    Args:
        df: DataFrame cu datele preprocesate
        seq_length: lungimea secvenței (câte zile anterioare folosim pentru predicție)
    Returns:
        X: secvențele de intrare
        y: valorile țintă (prețul de închidere pentru ziua următoare)
    """

    X, y = [], []

    # Selectăm coloanele pe care le vom folosi ca features
    features = df.values

    for i in range(len(df) - seq_length):
        X.append(features[i:i+seq_length])
        # Folosim doar prețul de închidere ca țintă
        y.append(features[i+seq_length, df.columns.get_loc('Close')])

    return np.array(X), np.array(y)

def prepare_data_for_lstm(ticker, start_date, end_date, seq_length=60):
    """
    Funcție principală care preprocesează datele pentru modelul LSTM
    """

    # Obtinem datele
    df = create_prices_dataframe_of_company(ticker, start_date, end_date)

    # Adaugam indicatorii tehnici
    df = add_technical_indicators(df)

    # Normalizam datele
    df_normalized, scaler = normalize_date(df)

    # Cream secventele pentru LSTM
    X, y = create_sequences(df_normalized, seq_length)

    # Impartim datel in set de antrenamet si test (80% train, 20% test)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    return X_train, X_test, y_train, y_test, scaler, df

