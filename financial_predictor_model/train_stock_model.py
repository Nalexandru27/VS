import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Importăm modulele create anterior
from data_preprocessing import prepare_data_for_lstm, add_technical_indicators
from lstm_model import StockPriceLSTM
from sentiment_analysis import get_price_with_sentiment

def train_lstm_model_with_sentiment(ticker, start_date, end_date, sequence_length=60, epochs=50):
    """
    Antrenează un model LSTM îmbunătățit cu date de sentiment
    """
    print(f"Începem antrenarea modelului pentru {ticker}...")
    
    # Obținem datele de preț cu sentiment
    combined_df = get_price_with_sentiment(ticker, start_date, end_date)
    
    # Adăugăm indicatorii tehnici
    df_with_indicators = add_technical_indicators(combined_df)
    
    # Pregătim datele pentru LSTM (reutilizând funcția, dar trimitem direct dataframe-ul nostru)
    print("Pregătim datele pentru antrenament...")
    X_train, X_test, y_train, y_test, scaler, _ = prepare_data_for_lstm(
        ticker, start_date, end_date, sequence_length
    )
    
    # Inițializăm și antrenăm modelul
    print("Inițializăm modelul LSTM...")
    model = StockPriceLSTM(sequence_length=sequence_length)
    
    print("Începem antrenamentul...")
    history = model.train(ticker, start_date, end_date, epochs=epochs)
    
    # Evaluăm modelul
    print("Evaluăm modelul...")
    loss = model.evaluate(X_test, y_test)
    print(f"Loss pe setul de test: {loss}")
    
    # Vizualizăm rezultatele
    print("Vizualizăm istoria antrenamentului...")
    model.plot_training_history()
    
    print("Vizualizăm predicțiile...")
    model.plot_predictions(ticker, start_date, end_date)
    
    # Salvăm modelul
    model_dir = os.path.join(os.path.dirname(__file__), "saved_models")
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, f"{ticker}_lstm_model.h5")
    model.save_model(model_path)
    
    return model

def analyze_cycle_patterns(ticker, model, start_date, end_date):
    """
    Analizează tiparele ciclice din prețurile și predicțiile modelului
    """
    # Implementare de bază - putem extinde ulterior
    from data_preprocessing import create_prices_dataframe_of_company
    
    # Obținem datele de preț
    price_df = create_prices_dataframe_of_company(ticker, start_date, end_date)
    
    # Calculăm medii mobile pentru a identifica tendințe
    price_df['MA50'] = price_df['Close Price'].rolling(window=50).mean()
    price_df['MA200'] = price_df['Close Price'].rolling(window=200).mean()
    
    # Identificăm punctele de încrucișare (golden cross, death cross)
    price_df['Golden_Cross'] = (price_df['MA50'] > price_df['MA200']) & (price_df['MA50'].shift(1) <= price_df['MA200'].shift(1))
    price_df['Death_Cross'] = (price_df['MA50'] < price_df['MA200']) & (price_df['MA50'].shift(1) >= price_df['MA200'].shift(1))
    
    # Identificăm tendințele pe termen lung
    price_df['Uptrend'] = price_df['MA50'] > price_df['MA200']
    
    # Calculăm randamentele lunare pentru a identifica sezonalitate
    price_df['Month'] = pd.to_datetime(price_df.index).month

    # Calculam randamentul zilnic
    price_df['Daily Return'] = price_df['Close Price'].pct_change()

    # Randamentele medii lunare
    monthly_returns = price_df.groupby('Month')['Daily Return'].mean()
    
    # Vizualizăm randamentele lunare pentru a identifica sezonalitate
    plt.figure(figsize=(12, 6))
    monthly_returns.plot(kind='bar', color='skyblue')
    plt.title(f'Randamente medii lunare pentru {ticker}')
    plt.xlabel('Luna')
    plt.ylabel('Randament mediu')
    plt.grid(True, alpha=0.3)
    plt.show()
    
    # Numărăm câte golden cross-uri și death cross-uri am avut
    golden_cross_count = price_df['Golden_Cross'].sum()
    death_cross_count = price_df['Death_Cross'].sum()
    
    print(f"\n=== Analiza ciclurilor pentru {ticker} ===")
    print(f"Număr de Golden Cross-uri: {golden_cross_count}")
    print(f"Număr de Death Cross-uri: {death_cross_count}")
    
    # Identificăm lunile cu cele mai bune și cele mai slabe performanțe
    best_month = monthly_returns.idxmax()
    worst_month = monthly_returns.idxmin()
    
    print(f"Luna cu cel mai bun randament mediu: {best_month} ({monthly_returns[best_month]:.2%})")
    print(f"Luna cu cel mai slab randament mediu: {worst_month} ({monthly_returns[worst_month]:.2%})")
    
    # Calculăm procentul de timp în trend ascendent
    uptrend_pct = price_df['Uptrend'].mean() * 100
    print(f"Procent de timp în trend ascendent: {uptrend_pct:.2f}%")
    
    return price_df

if __name__ == "__main__":
    # Exemplu de utilizare
    ticker = "GPC"  # Înlocuiți cu ticker-ul dorit
    start_date = "2013-01-01"
    end_date = "2025-04-29"
    
    # Antrenăm modelul
    model = train_lstm_model_with_sentiment(ticker, start_date, end_date)
    
    # Analizăm tiparele ciclice
    analysis_df = analyze_cycle_patterns(ticker, model, start_date, end_date)