import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.metrics import mean_squared_error, mean_absolute_error
import datetime

# Adăugăm calea proiectului la PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.DatabaseCRUD import DatabaseCRUD

# Importăm modulele create anterior
from lstm_model import StockPriceLSTM
from data_preprocessing import prepare_data_for_lstm, create_prices_dataframe_of_company, add_technical_indicators
from sentiment_analysis import get_price_with_sentiment

def load_and_test_model(ticker, model_path, start_date, end_date, sequence_length=60):
    """
    Încarcă un model salvat și îl testează pe date noi
    """
    print(f"Încărcăm modelul pentru {ticker}...")
    model = StockPriceLSTM.load_model(model_path, sequence_length)
    
    # Pregătim datele de test
    print("Pregătim datele de test...")
    _, X_test, _, y_test, scaler, df = prepare_data_for_lstm(
        ticker, start_date, end_date, sequence_length
    )
    
    print(df.head())

    # Facem predicții
    print("Generăm predicții...")
    predictions = model.predict(X_test)
    
    # Calculăm metricile de performanță
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, predictions)
    
    print(f"\n=== Metricile de performanță pentru {ticker} ===")
    print(f"Mean Squared Error (MSE): {mse:.6f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
    print(f"Mean Absolute Error (MAE): {mae:.6f}")
    
    # Vizualizăm predicțiile
    test_dates = df.index[-len(y_test):]

    test_dates = pd.to_datetime(test_dates)

    plt.figure(figsize=(18, 8))
    plt.plot(test_dates, y_test, label='Prețuri reale', color='blue')
    plt.plot(test_dates, predictions, label='Predicții', color='red')
    plt.title(f'Predicții LSTM pentru {ticker}')
    plt.xlabel('Data')
    plt.ylabel('Preț (normalizat)')
    plt.legend()
    plt.grid(True)

    # Formatăm axa X pentru lizibilitate
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()
    
    return model, y_test, predictions, test_dates

def detect_market_regime(df, window=50):
    """
    Detectează regimul de piață (bull market, bear market, sideways)
    """
    # Calculăm tendința pe baza mediilor mobile
    df['MA20'] = df['Close Price'].rolling(window=20).mean()
    df['MA50'] = df['Close Price'].rolling(window=50).mean()
    
    # Calculăm volatilitatea
    df['Volatility'] = df['Close Price'].rolling(window=window).std()
    
    # Detectăm regimul de piață
    df['Bull_Market'] = (df['MA20'] > df['MA50']) & (df['MA20'].shift(20) > df['MA50'].shift(20))
    df['Bear_Market'] = (df['MA20'] < df['MA50']) & (df['MA20'].shift(20) < df['MA50'].shift(20))
    df['Sideways'] = ~(df['Bull_Market'] | df['Bear_Market'])
    
    # Calculăm distribuția regimurilor
    regime_distribution = {
        'Bull_Market': df['Bull_Market'].mean() * 100,
        'Bear_Market': df['Bear_Market'].mean() * 100,
        'Sideways': df['Sideways'].mean() * 100
    }
    
    return df, regime_distribution

def analyze_model_performance_by_regime(ticker, y_test, predictions, df):
    """
    Analizează performanța modelului în funcție de regimul de piață
    """
    # Detectăm regimurile de piață
    df_with_regimes, regime_distribution = detect_market_regime(df)
    
    # Obținem regimurile corespunzătoare momentelor de test
    test_indices = df_with_regimes.index[-len(y_test):]
    test_regimes = df_with_regimes.loc[test_indices, ['Bull_Market', 'Bear_Market', 'Sideways']]
    
    # Calculăm eroarea pe fiecare regim
    bull_indices = test_regimes['Bull_Market']
    bear_indices = test_regimes['Bear_Market']
    sideways_indices = test_regimes['Sideways']
    
    bull_mse = mean_squared_error(y_test[bull_indices], predictions[bull_indices]) if bull_indices.any() else np.nan
    bear_mse = mean_squared_error(y_test[bear_indices], predictions[bear_indices]) if bear_indices.any() else np.nan
    sideways_mse = mean_squared_error(y_test[sideways_indices], predictions[sideways_indices]) if sideways_indices.any() else np.nan
    
    print(f"\n=== Distribuția regimurilor de piață ===")
    print(f"Bull Market: {regime_distribution['Bull_Market']:.2f}%")
    print(f"Bear Market: {regime_distribution['Bear_Market']:.2f}%")
    print(f"Sideways: {regime_distribution['Sideways']:.2f}%")
    
    print(f"\n=== Performanța modelului pe regimuri ===")
    print(f"MSE în Bull Market: {bull_mse:.6f}")
    print(f"MSE în Bear Market: {bear_mse:.6f}")
    print(f"MSE în Sideways: {sideways_mse:.6f}")
    
    # Vizualizăm performanța pe regimuri
    plt.figure(figsize=(10, 6))
    regime_mse = [bull_mse, bear_mse, sideways_mse]
    regime_names = ['Bull Market', 'Bear Market', 'Sideways']
    
    plt.bar(regime_names, regime_mse, color=['green', 'red', 'blue'])
    plt.title(f'MSE per regim de piață pentru {ticker}')
    plt.ylabel('Mean Squared Error')
    plt.grid(True, alpha=0.3)
    plt.show()
    
    return bull_mse, bear_mse, sideways_mse

def predict_future_prices(ticker, model_path, days_to_predict=5, sequence_length=60):
    """
    Predicts future stock prices using a trained LSTM model
    Numărul implicit de zile a fost redus la 5 zile
    """
    print(f"Predicting future prices for {ticker} for the next {days_to_predict} days...")
    
    # Load the trained model
    model = StockPriceLSTM.load_model(model_path, sequence_length)
    
    # First, check if we have any data in the database for this ticker
    # Let's try to get data for the past year to verify our database has entries
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    two_years_ago = (datetime.datetime.now() - datetime.timedelta(days=2*365)).strftime('%Y-%m-%d')
    
    print(f"Verifying data availability from {two_years_ago} to {today}")
    
    # Create the dataframe to check data availability
    df_check = create_prices_dataframe_of_company(ticker, two_years_ago, today)
    
    if len(df_check) == 0:
        print(f"Error: No data found for {ticker} in the database for the past two years.")
        print("Please make sure your database has stock price data for this ticker.")
        return None
    
    print(f"Found {len(df_check)} data points for {ticker} in the database.")
    print(f"Data range: {df_check.index[0]} to {df_check.index[-1]}")
    
    # Verifică și convertește indexul în obiecte datetime dacă este necesar
    if isinstance(df_check.index[0], str):
        # Convertește indexul din string în datetime
        df_check.index = pd.to_datetime(df_check.index)
    
    # Use the available data range instead of arbitrary dates
    start_date = df_check.index[0].strftime('%Y-%m-%d')
    end_date = df_check.index[-1].strftime('%Y-%m-%d')
    
    print(f"Using data range from {start_date} to {end_date}")
    
    # În loc să folosim doar add_technical_indicators, vom adăuga manual toți indicatorii folosiți la antrenare
    df = df_check.copy()
    
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
    
    # Normalize the data manually
    from sklearn.preprocessing import MinMaxScaler
    
    # Create a copy of the dataframe to avoid SettingWithCopyWarning
    df_normalized = df.copy()
    
    # Initialize scaler for Close Price and other features
    scaler_close = MinMaxScaler(feature_range=(0, 1))
    scaler_features = MinMaxScaler(feature_range=(0, 1))
    
    # Make sure we have data before fitting the scaler
    if len(df) == 0:
        print("Error: No data available after preprocessing.")
        return None
    
    # Normalize 'Close Price' column
    df_normalized['Close Price'] = scaler_close.fit_transform(df[['Close Price']])
    
    # Lista caracteristicilor utilizate în antrenament (actualizată conform noilor indicatori)
    possible_features = [
        'Close Price', 'MA5', 'MA20', 'MA50', 'MA200', 'RSI', 'Volatility', 'Daily_Return'
    ]
    
    # Identifică care caracteristici sunt disponibile în dataframe
    available_features = [col for col in possible_features if col in df.columns]
    
    # Înlocuim valorile NaN cu 0 pentru a evita probleme în timpul normalizării
    for feature in available_features:
        if feature != 'Close Price':  # Am normalizat deja Close Price
            if feature in df.columns:
                df_normalized[feature] = df_normalized[feature].fillna(0)
                
                # Normalizăm caracteristica dacă conține valori numerice
                if df_normalized[feature].dtype in ['float64', 'int64', 'float32', 'int32']:
                    # Reshape pentru a se potrivi cu API-ul MinMaxScaler
                    values = df_normalized[feature].values.reshape(-1, 1)
                    df_normalized[feature] = scaler_features.fit_transform(values).flatten()
    
    # Check if we have enough data for the sequence length
    if len(df_normalized) < sequence_length:
        print(f"Error: Not enough data points ({len(df_normalized)}) for the required sequence length ({sequence_length}).")
        print(f"Consider reducing sequence_length or obtaining more data.")
        return None
    
    # Afișăm caracteristicile disponibile pentru informare
    print(f"Available features: {available_features}")
    
    # IMPORTANT: Determină numărul de caracteristici din model
    # Extragem forma modelului din primul strat
    try:
        # First try to access through model.model structure
        input_shape = model.model.input_shape
        num_features_in_model = input_shape[-1]  # Last dimension is the number of features
    except AttributeError:
        try:
            # Try direct access if model doesn't have nested structure
            input_shape = model.input_shape
            num_features_in_model = input_shape[-1]
        except AttributeError:
            # If both approaches fail, try to get it from the first layer's input shape
            if hasattr(model, 'model') and hasattr(model.model, 'layers'):
                input_shape = model.model.layers[0].input_shape
                num_features_in_model = input_shape[-1]
            elif hasattr(model, 'layers'):
                input_shape = model.layers[0].input_shape
                num_features_in_model = input_shape[-1]
            else:
                # If all attempts fail, use a fallback approach
                print("Could not determine model's input shape automatically.")
                print("Using the number of available features as a fallback.")
                num_features_in_model = len(available_features)
    
    print(f"Number of features expected by the model: {num_features_in_model}")
    
    # Verificăm dacă avem suficiente caracteristici
    if len(available_features) < num_features_in_model:
        print(f"Warning: Model expects {num_features_in_model} features, but only {len(available_features)} are available.")
        print("Adding dummy features to match the expected input shape.")
        
        # Adăugăm caracteristici dummy dacă este necesar
        for i in range(len(available_features), num_features_in_model):
            feature_name = f"dummy_feature_{i}"
            df_normalized[feature_name] = 0.0
            available_features.append(feature_name)
    elif len(available_features) > num_features_in_model:
        print(f"Warning: There are {len(available_features)} available features, but the model expects only {num_features_in_model}.")
        print(f"Using only the first {num_features_in_model} features.")
        available_features = available_features[:num_features_in_model]
    
    # Selectăm primele num_features_in_model caracteristici pentru a se potrivi cu modelul
    feature_cols = available_features[:num_features_in_model]
    print(f"Using features: {feature_cols}")
    
    # Prepare sequences for LSTM
    X = []
    y = []
    
    for i in range(sequence_length, len(df_normalized)):
        X.append(df_normalized.iloc[i-sequence_length:i][feature_cols].values)
        y.append(df_normalized.iloc[i]['Close Price'])
    
    # Convert to numpy arrays
    X = np.array(X)
    y = np.array(y)
    
    # Get the most recent sequence for prediction
    recent_data = df_normalized.tail(sequence_length)[feature_cols].values
    X_recent = np.array([recent_data])
    
    print(f"X_recent shape: {X_recent.shape}")
    
    # Initialize prediction array
    future_predictions = []
    current_input = X_recent.copy()
    
    # Generate predictions iteratively
    for i in range(days_to_predict):
        # Predict the next day
        next_pred = model.model.predict(current_input, verbose=0)
        
        # Append to our predictions list
        future_predictions.append(next_pred[0, 0])
        
        # Update the input window for the next prediction
        # Creăm o nouă linie cu toate caracteristicile
        new_row = np.zeros((1, num_features_in_model))
        
        # Setăm valoarea pentru 'Close Price' și menținem celelalte caracteristici la ultima valoare cunoscută
        close_price_index = feature_cols.index('Close Price') if 'Close Price' in feature_cols else 0
        
        # Copiem ultima linie pentru toate caracteristicile
        new_row[0, :] = current_input[0, -1, :]
        
        # Actualizăm doar prețul de închidere cu valoarea prezisă
        new_row[0, close_price_index] = next_pred[0, 0]
        
        # Shift the window and add the new prediction
        current_input[0, :-1, :] = current_input[0, 1:, :]
        current_input[0, -1:, :] = new_row
    
    # Convert predictions back to original scale
    future_predictions_array = np.array(future_predictions).reshape(-1, 1)
    future_prices = scaler_close.inverse_transform(future_predictions_array)
    
    # Generate future dates (only business days)
    last_date = pd.to_datetime(df.index[-1])
    future_dates = []
    current_date = last_date
    count = 0
    
    while count < days_to_predict:
        current_date += datetime.timedelta(days=1)
        # Skip weekends
        if current_date.weekday() < 5:  # Monday to Friday
            future_dates.append(current_date)
            count += 1
        if count >= days_to_predict:
            break
    
    # Make sure we have the right number of dates
    future_dates = future_dates[:days_to_predict]
    
    # Create a dataframe with the predictions
    future_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Price': future_prices.flatten()
    })
    
    # Display the predictions
    print("\n=== Future Price Predictions ===")
    print(future_df)
    
    # Plot the historical prices and future predictions
    plt.figure(figsize=(16, 8))

    # Obține ultima dată și preț din datele istorice
    last_historical_date = df.index[-1]
    last_historical_price = df['Close Price'].iloc[-1]

    # Adaugă ultima valoare istorică la începutul predicțiilor
    combined_dates = [last_historical_date] + list(future_df['Date'])
    combined_prices = [last_historical_price] + list(future_df['Predicted_Price'])

    # Plotează datele istorice
    plt.plot(df.index[-60:], df['Close Price'].tail(60), label='Historical Prices', color='blue')

    # Plotează predicțiile începând de la ultimul punct istoric
    plt.plot(combined_dates, combined_prices, label='Predicted Prices', color='red', linestyle='--')

    plt.title(f'Future Price Predictions for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    return future_df

if __name__ == "__main__":
    # Exemplu de utilizare
    ticker = "GPC"  # Înlocuiți cu ticker-ul dorit
    start_date = "2013-01-01"
    end_date = "2025-04-29"
    
    # Calea către modelul salvat
    model_dir = os.path.join(os.path.dirname(__file__), "saved_models")
    model_path = os.path.join(model_dir, f"{ticker}_lstm_model.h5")
    
    # Verificăm dacă modelul există
    if os.path.exists(model_path):
        # Testăm modelul
        model, y_test, predictions, test_dates = load_and_test_model(
            ticker, model_path, start_date, end_date
        )
        
        # Obținem datele pentru analiză
        df = create_prices_dataframe_of_company(ticker, start_date, end_date)
        
        # Analizăm performanța modelului pe diferite regimuri de piață
        bull_mse, bear_mse, sideways_mse = analyze_model_performance_by_regime(
            ticker, y_test, predictions, df
        )

         # Predict future prices
        future_predictions = predict_future_prices(ticker, model_path)
    else:
        print(f"Nu s-a găsit modelul salvat pentru {ticker}. Rulați mai întâi script-ul de antrenare.")