import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import os
import time

# Descărcăm resursele necesare pentru NLTK (doar la prima rulare)
try:
    nltk.data.find('vader_lexicon')
except:
    nltk.download('vader_lexicon')

class StockSentimentAnalyzer:
    def __init__(self, api_key=None):
        """
        Inițializează analizatorul de sentiment
        Args:
            api_key: Cheia API pentru serviciile de știri (opțional)
        """
        self.sia = SentimentIntensityAnalyzer()
        self.api_key = api_key

    def get_sentiment_score(self, text):
        """
        Calculează scorul de sentiment pentru un text
        """
        if not text or not isinstance(text, str):
            return {'compound': 0, 'neg': 0, 'neu': 0, 'pos': 0}
        
        sentiment = self.sia.polarity_scores(text)
        return sentiment
    
    def fetch_news(self, ticker, start_date, end_date):
        """
        Obține știri pentru un anumit ticker în intervalul de date specificat
        Notă: Această funcție necesită un API key pentru un serviciu de știri financiare
        """

        # Dacă nu avem API key, returnăm date simulate
        if not self.api_key:
            print("Nu s-a furnizat API key. Se generează date simulate de sentiment.")
            return self._generate_simulated_news_data(ticker, start_date, end_date)
            
        # Aici ar trebui implementată logica pentru a prelua știri reale folosind API
        # (exemplu: Alpha Vantage, NewsAPI, etc.)
        pass

    def _generate_simulated_news_data(self, ticker, start_date, end_date):
        """
        Generează date simulate de știri pentru testare
        """
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        date_range = pd.date_range(start=start, end=end, freq='B')  # Doar zile de tranzacționare
        
        news_data = []
        for date in date_range:
            # Simulăm 0-3 știri pe zi
            num_news = np.random.randint(0, 4)
            for _ in range(num_news):
                # Generăm sentiment aleator, înclinat puțin spre pozitiv
                sentiment = np.random.normal(0.1, 0.5)  # Media 0.1, std dev 0.5
                sentiment = max(min(sentiment, 1.0), -1.0)  # Limităm la [-1, 1]
                
                news_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'ticker': ticker,
                    'headline': f'Simulated news for {ticker}',
                    'sentiment_score': sentiment
                })
        
        return pd.DataFrame(news_data)
    
    def analyze_ticker_sentiment(self, ticker, start_date, end_date):
        """
        Analizează sentimentul general pentru un ticker în perioada specificată
        """
        # Obținem știrile
        news_df = self.fetch_news(ticker, start_date, end_date)
        
        if news_df.empty:
            print(f"Nu s-au găsit știri pentru {ticker}")
            return pd.DataFrame()
        
        # Agregăm sentimentul pe zile
        daily_sentiment = news_df.groupby('date').agg({
            'sentiment_score': ['mean', 'count', 'std']
        })
        
        # Simplificăm structura coloanelor
        daily_sentiment.columns = ['sentiment_mean', 'news_count', 'sentiment_std']
        daily_sentiment = daily_sentiment.reset_index()
        
        # Convertim data la format datetime
        daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])
        daily_sentiment = daily_sentiment.set_index('date')
        
        return daily_sentiment
    
    def combine_price_and_sentiment(self, price_df, sentiment_df):
        """
        Combină datele de preț cu analiza de sentiment
        """
        # Asigurăm-ne că price_df are index de tip datetime
        if not isinstance(price_df.index, pd.DatetimeIndex):
            price_df.index = pd.to_datetime(price_df.index)
            
        # Ne asigurăm că sentiment_df are index de tip datetime    
        if not isinstance(sentiment_df.index, pd.DatetimeIndex):
            sentiment_df.index = pd.to_datetime(sentiment_df.index)
        
        # Combinăm dataframe-urile
        combined_df = price_df.join(sentiment_df, how='left')
        
        # Completăm valorile lipsă din sentimente cu 0 (neutru)
        sentiment_cols = ['sentiment_mean', 'news_count', 'sentiment_std']
        for col in sentiment_cols:
            if col in combined_df.columns:
                combined_df[col] = combined_df[col].fillna(0)
        
        return combined_df
    
def get_price_with_sentiment(ticker, start_date, end_date):
    """
    Obține datele de preț împreună cu analiza de sentiment
    """
    from data_preprocessing import create_prices_dataframe_of_company
    
    # Obținem datele de preț
    price_df = create_prices_dataframe_of_company(ticker, start_date, end_date)
        
    # Analizăm sentimentul
    sentiment_analyzer = StockSentimentAnalyzer()
    sentiment_df = sentiment_analyzer.analyze_ticker_sentiment(ticker, start_date, end_date)
        
    # Combinăm datele
    combined_df = sentiment_analyzer.combine_price_and_sentiment(price_df, sentiment_df)
        
    return combined_df
    
