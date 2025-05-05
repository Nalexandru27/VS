import pandas as pd
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
from datetime import datetime, timedelta
import time
import os
import json
from tqdm import tqdm
import re

# Descărcăm resursele necesare pentru NLTK (doar la prima rulare)
try:
    nltk.data.find('vader_lexicon')
except:
    nltk.download('vader_lexicon')

class EnhancedSentimentAnalyzer:
    def __init__(self, api_key=None):
        """
        Inițializează analizatorul îmbunătățit de sentiment
        Args:
            api_key: Cheia API pentru News API
        """
        self.sia = SentimentIntensityAnalyzer()
        self.api_key = api_key
        self.cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_sentiment_score(self, text):
        """
        Calculează scorul de sentiment pentru un text
        """
        if not text or not isinstance(text, str):
            return {'compound': 0, 'neg': 0, 'neu': 0, 'pos': 0}
            
        sentiment = self.sia.polarity_scores(text)
        return sentiment
    
    def get_cached_news(self, ticker, start_date, end_date):
        """
        Verifică dacă avem deja știri în cache pentru acest ticker și perioadă
        """
        cache_file = os.path.join(self.cache_dir, f"{ticker}_{start_date}_{end_date}_news.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return pd.DataFrame(json.load(f))
        return None
    
    def save_news_to_cache(self, ticker, start_date, end_date, news_df):
        """
        Salvează știrile în cache pentru utilizări ulterioare
        """
        cache_file = os.path.join(self.cache_dir, f"{ticker}_{start_date}_{end_date}_news.json")
        
        with open(cache_file, 'w') as f:
            json.dump(news_df.to_dict('records'), f)
    
    def fetch_news_from_api(self, ticker, start_date, end_date):
        """
        Obține știri pentru un anumit ticker folosind News API
        """
        if not self.api_key:
            print("Nu s-a furnizat API key pentru News API. Se generează date simulate.")
            return self._generate_simulated_news_data(ticker, start_date, end_date)
        
        # Transformăm datele în formatul cerut de API
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # News API limitează căutarea la 30 de zile, așa că trebuie să împărțim în intervale
        all_articles = []
        current_start = start
        
        with tqdm(total=(end - start).days, desc="Colectare știri") as pbar:
            while current_start < end:
                current_end = min(current_start + timedelta(days=29), end)
                
                # Formatăm datele pentru API
                from_date = current_start.strftime('%Y-%m-%d')
                to_date = current_end.strftime('%Y-%m-%d')
                
                # Construim URL-ul pentru cerere
                url = (
                    f"https://newsapi.org/v2/everything?"
                    f"q={ticker} stock OR shares OR company OR earnings&"
                    f"from={from_date}&"
                    f"to={to_date}&"
                    f"language=en&"
                    f"sortBy=publishedAt&"
                    f"apiKey={self.api_key}"
                )
                
                try:
                    # Facem cererea la API
                    response = requests.get(url)
                    response_json = response.json()
                    
                    if response.status_code == 200 and response_json.get('status') == 'ok':
                        articles = response_json.get('articles', [])
                        all_articles.extend(articles)
                        
                        # Actualizăm progress bar-ul
                        pbar.update((current_end - current_start).days)
                        
                        # Așteptăm pentru a respecta limitele API-ului
                        time.sleep(1)
                    else:
                        print(f"Eroare la obținerea știrilor: {response_json.get('message', 'Eroare necunoscută')}")
                        break
                except Exception as e:
                    print(f"Excepție la obținerea știrilor: {str(e)}")
                    break
                
                # Trecem la următorul interval
                current_start = current_end + timedelta(days=1)
        
        # Procesăm articolele obținute
        news_data = []
        for article in all_articles:
            published_at = article.get('publishedAt')
            if published_at:
                date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
                
                # Combinăm titlul și descrierea pentru analiza de sentiment
                text = " ".join(filter(None, [article.get('title', ''), article.get('description', '')]))
                
                # Calculăm scorul de sentiment
                sentiment = self.get_sentiment_score(text)
                
                news_data.append({
                    'date': date,
                    'ticker': ticker,
                    'headline': article.get('title', ''),
                    'content': article.get('description', ''),
                    'url': article.get('url', ''),
                    'sentiment_score': sentiment['compound'],
                    'sentiment_neg': sentiment['neg'],
                    'sentiment_neu': sentiment['neu'],
                    'sentiment_pos': sentiment['pos']
                })
        
        news_df = pd.DataFrame(news_data)
        return news_df
    
    def _generate_simulated_news_data(self, ticker, start_date, end_date):
        """
        Generează date simulate de știri pentru testare
        Îmbunătățit cu mai multe detalii și mai realist
        """
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        date_range = pd.date_range(start=start, end=end, freq='B')  # Doar zile de tranzacționare
        
        # Evenimente financiare comune
        financial_events = [
            "Quarterly Earnings Report", "Annual Shareholder Meeting", 
            "Product Launch", "Executive Change", "Merger Announcement",
            "Dividend Announcement", "Stock Split", "Market Expansion",
            "New Partnership", "Industry Award", "Regulatory Approval",
            "Legal Settlement", "Research Breakthrough", "Analyst Upgrade",
            "Analyst Downgrade", "Market Share Gain", "Cost Cutting Initiative"
        ]
        
        # Modele de titluri
        title_templates = [
            "{ticker} announces {event}",
            "{ticker} shares {movement} after {event}",
            "Investors react to {ticker}'s {event}",
            "{ticker} stock {movement} on {event} news",
            "Analysts {opinion} {ticker} following {event}",
            "{ticker} {movement} to {value_change}% as {event} impacts market",
            "Breaking: {ticker} {event} exceeds expectations",
            "Report: {ticker}'s {event} suggests {outlook} outlook"
        ]
        
        # Paternuri pentru evoluția sentimentului (simulare trend, evenimente, etc.)
        # Folosim funcții trigonometrice pentru a simula tendințe și sezonalitate
        day_count = (end - start).days
        base_sentiment = np.sin(np.linspace(0, 6*np.pi, day_count)) * 0.3  # Trend de bază
        
        # Adăugăm o componentă aleatoare pentru realism
        noise = np.random.normal(0, 0.4, day_count)
        sentiment_trend = base_sentiment + noise
        sentiment_trend = np.clip(sentiment_trend, -1.0, 1.0)  # Limităm la [-1, 1]
        
        # Simulăm evenimente majore (spike-uri în sentiment)
        major_events = np.random.choice([0, 1], day_count, p=[0.97, 0.03])  # 3% șanse pentru evenimente majore
        for i in range(day_count):
            if major_events[i] == 1:
                # Eveniment major - generează un spike
                direction = np.random.choice([-1, 1])
                spike_magnitude = np.random.uniform(0.4, 0.8) * direction
                
                # Afectează 5 zile în jurul evenimentului
                for j in range(max(0, i-2), min(day_count, i+3)):
                    if j != i:
                        decay = 1 - abs(j - i) * 0.3  # Efectul scade cu distanța
                        sentiment_trend[j] += spike_magnitude * decay
                
                sentiment_trend[i] += spike_magnitude
        
        # Clipăm din nou pentru a fi siguri că rămânem în [-1, 1]
        sentiment_trend = np.clip(sentiment_trend, -1.0, 1.0)
        
        # Generăm știri pe baza trend-ului de sentiment
        news_data = []
        day_idx = 0
        
        for date in date_range:
            # Determinăm câte știri generăm pentru această zi (mai multe în zile cu sentiment extremal)
            sentiment_magnitude = abs(sentiment_trend[day_idx])
            base_count = 1 if sentiment_magnitude < 0.3 else (2 if sentiment_magnitude < 0.6 else 3)
            num_news = np.random.poisson(base_count)
            
            for _ in range(num_news):
                # Alegem un eveniment
                event = np.random.choice(financial_events)
                
                # Determinăm direcția și magnitudinea "mișcării" prețului
                sentiment = sentiment_trend[day_idx]
                
                # Selectăm termeni bazați pe sentiment
                if sentiment > 0.3:
                    movement = np.random.choice(["rises", "jumps", "surges", "climbs", "soars"])
                    opinion = np.random.choice(["praise", "upgrade", "recommend", "endorse"])
                    outlook = np.random.choice(["positive", "optimistic", "strong", "promising"])
                    value_change = np.random.uniform(1, 5)
                elif sentiment < -0.3:
                    movement = np.random.choice(["falls", "drops", "plunges", "declines", "tumbles"])
                    opinion = np.random.choice(["criticize", "downgrade", "question", "cautious about"])
                    outlook = np.random.choice(["negative", "pessimistic", "weak", "concerning"])
                    value_change = -np.random.uniform(1, 5)
                else:
                    movement = np.random.choice(["fluctuates", "holds steady", "remains stable", "trades sideways"])
                    opinion = np.random.choice(["analyze", "review", "examine", "assess"])
                    outlook = np.random.choice(["mixed", "neutral", "balanced", "uncertain"])
                    value_change = np.random.uniform(-1, 1)
                
                # Generăm titlul
                template = np.random.choice(title_templates)
                headline = template.format(
                    ticker=ticker,
                    event=event,
                    movement=movement,
                    opinion=opinion,
                    outlook=outlook,
                    value_change=round(value_change, 1)
                )
                
                # Adăugăm un sentiment puțin diferit de trend pentru realism
                noise = np.random.normal(0, 0.1)
                article_sentiment = np.clip(sentiment + noise, -1.0, 1.0)
                
                # Calculăm componentele pozitivă, negativă și neutră
                if article_sentiment > 0:
                    pos = 0.5 + article_sentiment/2
                    neg = 0.5 - article_sentiment/2
                    neu = 1.0 - pos - neg
                else:
                    neg = 0.5 - article_sentiment/2
                    pos = 0.5 + article_sentiment/2
                    neu = 1.0 - pos - neg
                
                # Ajustăm pentru a avea o sumă de 1
                total = pos + neg + neu
                pos, neg, neu = pos/total, neg/total, neu/total
                
                news_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'ticker': ticker,
                    'headline': headline,
                    'content': f"Simulated news content for {headline}",
                    'url': 'https://example.com/simulated-news',
                    'sentiment_score': article_sentiment,
                    'sentiment_neg': neg,
                    'sentiment_neu': neu,
                    'sentiment_pos': pos
                })
            
            day_idx += 1
            if day_idx >= len(sentiment_trend):
                break
        
        return pd.DataFrame(news_data)
    
    def get_news(self, ticker, start_date, end_date):
        """
        Obține știri pentru ticker în perioada specificată
        Prima verifică în cache, apoi încearcă API-ul
        """
        # Verificăm mai întâi cache-ul
        cached_news = self.get_cached_news(ticker, start_date, end_date)
        
        if cached_news is not None:
            print(f"Folosind date din cache pentru {ticker} ({start_date} - {end_date})")
            return cached_news
        
        # Dacă nu avem în cache, obținem de la API sau generăm simulate
        news_df = self.fetch_news_from_api(ticker, start_date, end_date)
        
        # Salvăm rezultatele în cache
        self.save_news_to_cache(ticker, start_date, end_date, news_df)
        
        return news_df
    
    def analyze_sentiment_trends(self, ticker, start_date, end_date):
        """
        Analizează tendințele de sentiment pentru un ticker
        """
        # Obținem datele de știri
        news_df = self.get_news(ticker, start_date, end_date)
        
        if news_df.empty:
            print(f"Nu s-au găsit știri pentru {ticker}")
            return pd.DataFrame()
        
        # Convertim coloana de date la datetime
        news_df['date'] = pd.to_datetime(news_df['date'])
        
        # Agregăm sentimentul pe zile
        daily_sentiment = news_df.groupby('date').agg({
            'sentiment_score': ['mean', 'count', 'std'],
            'sentiment_pos': 'mean',
            'sentiment_neg': 'mean',
            'sentiment_neu': 'mean'
        })
        
        # Simplificăm structura coloanelor
        daily_sentiment.columns = [
            'sentiment_mean', 'news_count', 'sentiment_std',
            'sentiment_pos', 'sentiment_neg', 'sentiment_neu'
        ]
        
        # Adăugăm media mobilă pentru tendința generală
        daily_sentiment['sentiment_ma7'] = daily_sentiment['sentiment_mean'].rolling(window=7).mean()
        daily_sentiment['sentiment_ma30'] = daily_sentiment['sentiment_mean'].rolling(window=30).mean()
        
        # Detectăm schimbările majore în sentiment
        daily_sentiment['sentiment_shift'] = daily_sentiment['sentiment_mean'].diff()
        daily_sentiment['major_shift'] = abs(daily_sentiment['sentiment_shift']) > 0.3
        
        # Resetăm indexul pentru a avea data ca o coloană
        daily_sentiment = daily_sentiment.reset_index()
        
        return daily_sentiment
    
    def combine_sentiment_with_price(self, ticker, start_date, end_date, db_crud):
        """
        Combină analiza de sentiment cu datele de preț
        """
        from data_preprocessing import create_prices_dataframe_of_company
        
        # Obținem datele de preț
        price_df = create_prices_dataframe_of_company(ticker, start_date, end_date)

        if price_df is None or price_df.empty:
            print(f"Nu s-au putut obține datele de preț pentru {ticker}.")
            return None
        
        # Adăugăm randamentele
        price_df['Return'] = price_df['Close Price'].pct_change()
        
        # Obținem datele de sentiment
        sentiment_df = self.analyze_sentiment_trends(ticker, start_date, end_date)

        if sentiment_df is None or sentiment_df.empty:
            print(f"Nu s-au putut obține datele de sentiment pentru {ticker}.")
            return price_df.set_index('Date') # Returnează doar prețurile dacă nu sunt sentimente
        
        # Asigurăm-ne că ambele dataframe-uri au index de date
        price_df = price_df.reset_index()
        price_df['Date'] = pd.to_datetime(price_df['Date'])
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
        
        # Combinăm dataframe-urile
        combined_df = pd.merge(price_df, sentiment_df, left_on='Date', right_on='date', how='inner') # Important: inner join
        
        # Completăm valorile lipsă
        sentiment_cols = ['sentiment_mean', 'news_count', 'sentiment_std', 
                         'sentiment_pos', 'sentiment_neg', 'sentiment_neu',
                         'sentiment_ma7', 'sentiment_ma30']
        
        for col in sentiment_cols:
            if col in combined_df.columns:
                # Completăm cu ultimele valori cunoscute
                combined_df[col] = combined_df[col].ffill()
                # Pentru primele zile, folosim media
                combined_df[col] = combined_df[col].fillna(combined_df[col].mean())
        
        # Setăm data ca index
        combined_df = combined_df.set_index('Date')
        combined_df = combined_df.drop('date', axis=1, errors='ignore')
        
        return combined_df
    
    def plot_sentiment_analysis(self, ticker, start_date, end_date, db_crud):
        """
        Plotează analiza de sentiment împreună cu prețurile
        """
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        
        # Obținem datele combinate
        combined_df = self.combine_sentiment_with_price(ticker, start_date, end_date, db_crud)
        
        # Creăm o figură de dimensiuni mari
        fig, axes = plt.subplots(3, 1, figsize=(16, 18), sharex=True)
        
        # Plot 1: Prețul și media mobilă
        ax1 = axes[0]
        ax1.plot(combined_df.index, combined_df['Close Price'], 'b-', label='Preț de închidere')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylabel('Preț ($)')
        ax1.set_title(f'Preț și analiză de sentiment pentru {ticker}')
        ax1.legend(loc='upper left')
        
        # Plot 2: Sentimentul
        ax2 = axes[1]
        ax2.plot(combined_df.index, combined_df['sentiment_mean'], 'g-', alpha=0.7, label='Sentiment zilnic')
        ax2.plot(combined_df.index, combined_df['sentiment_ma7'], 'r-', label='Sentiment MA7')
        ax2.plot(combined_df.index, combined_df['sentiment_ma30'], 'k-', label='Sentiment MA30')
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        ax2.fill_between(combined_df.index, 0, combined_df['sentiment_mean'], 
                        where=combined_df['sentiment_mean'] >= 0, color='green', alpha=0.3)
        ax2.fill_between(combined_df.index, 0, combined_df['sentiment_mean'], 
                        where=combined_df['sentiment_mean'] < 0, color='red', alpha=0.3)
        ax2.set_ylabel('Scor de sentiment')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper left')
        ax2.set_ylim(-1, 1)
        
        # Plot 3: Numărul de știri
        ax3 = axes[2]
        ax3.bar(combined_df.index, combined_df['news_count'], color='blue', alpha=0.6)
        ax3.set_ylabel('Număr de știri')
        ax3.set_xlabel('Data')
        ax3.grid(True, alpha=0.3)
        
        # Formatăm axa x pentru date
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        return combined_df
    
    
    def analyze_sentiment_price_relationship(self, ticker, start_date, end_date, db_crud):
        """
        Analizează relația dintre sentiment și prețuri
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy.stats import pearsonr
        import numpy as np
        import pandas as pd

        # Obținem datele combinate
        combined_df = self.combine_sentiment_with_price(ticker, start_date, end_date, db_crud)

        if combined_df is None or combined_df.empty:
            print(f"Nu s-au putut combina datele de sentiment și preț pentru {ticker}.")
            return None

        # Eliminăm rândurile unde fie sentiment, fie randament este NaN
        filtered_df = combined_df[['sentiment_mean', 'Return']].dropna()

        sentiment_series = filtered_df['sentiment_mean']
        return_series = filtered_df['Return']

        print(f"Lungimea seriei de sentiment după dropna: {len(sentiment_series)}")
        print(f"Lungimea seriei de randamente după dropna: {len(return_series)}")

        correlation = None
        p_value = None

        if len(sentiment_series) > 1 and len(sentiment_series) == len(return_series):
            correlation, p_value = pearsonr(sentiment_series, return_series)
            print(f"\n=== Corelația dintre sentiment și randamente pentru {ticker} ===")
            print(f"Corelație Pearson: {correlation:.4f} (p-value: {p_value:.4f})")

            # Vizualizare scatter
            plt.figure(figsize=(10, 6))
            plt.scatter(sentiment_series, return_series, alpha=0.6)
            plt.title(f'Sentiment vs. Randament pentru {ticker} (r={correlation:.4f})')
            plt.xlabel('Sentiment Mediu Zilnic')
            plt.ylabel('Randament Zilnic')
            plt.grid(True)
            plt.show()
        else:
            print("\nNu se poate calcula corelația Pearson.")

        # Calculăm corelația cu lag-uri
        lags = range(1, 11)
        lag_correlations = []

        for lag in lags:
            lagged_sentiment = combined_df['sentiment_mean'].shift(lag)
            lag_corr = lagged_sentiment.corr(combined_df['Return'])
            lag_correlations.append(lag_corr)

        plt.figure(figsize=(12, 6))
        plt.bar(lags, lag_correlations, color='skyblue')
        plt.axhline(y=0, color='gray', linestyle='--')
        plt.xlabel('Lag (zile)')
        plt.ylabel('Corelație cu randamentul')
        plt.title(f'Corelația dintre sentiment și randament cu lag pentru {ticker}')
        plt.grid(True, alpha=0.3)
        plt.show()

        # Vizualizare generală scatter (chiar dacă corelația nu s-a calculat)
        plt.figure(figsize=(10, 8))
        plt.scatter(combined_df['sentiment_mean'], combined_df['Return'], alpha=0.5)
        plt.axhline(y=0, color='gray', linestyle='--')
        plt.axvline(x=0, color='gray', linestyle='--')
        plt.xlabel('Scor de sentiment')
        plt.ylabel('Randament zilnic')
        plt.title(f'Sentiment vs. Randament pentru {ticker}')
        plt.grid(True, alpha=0.3)
        plt.show()

        # Analizăm schimbările mari de sentiment
        if 'sentiment_shift' in combined_df.columns:
            sentiment_shifts = combined_df['sentiment_shift'].dropna()
            large_shifts = sentiment_shifts[abs(sentiment_shifts) > 0.2]

            if not large_shifts.empty:
                large_shift_dates = large_shifts.index
                future_returns = pd.DataFrame()

                for days in [1, 3, 5, 10]:
                    returns = []
                    for date in large_shift_dates:
                        try:
                            future_date = combined_df.index[combined_df.index.get_loc(date) + days]
                            future_price = combined_df.loc[future_date, 'Close Price']
                            current_price = combined_df.loc[date, 'Close Price']
                            future_return = (future_price / current_price - 1) * 100
                            returns.append(future_return)
                        except:
                            returns.append(np.nan)

                    future_returns[f'{days}-day return'] = returns

                future_returns['Sentiment Shift'] = large_shifts.values
                future_returns['Shift Direction'] = np.where(future_returns['Sentiment Shift'] > 0, 'Positive', 'Negative')

                plt.figure(figsize=(12, 6))
                pos_shifts = future_returns[future_returns['Shift Direction'] == 'Positive']
                neg_shifts = future_returns[future_returns['Shift Direction'] == 'Negative']

                cols = ['1-day return', '3-day return', '5-day return', '10-day return']

                if not pos_shifts.empty:
                    plt.boxplot(pos_shifts[cols].values, positions=np.array(range(len(cols)))*2-0.4, 
                            widths=0.6, labels=cols, patch_artist=True,
                            boxprops=dict(facecolor='green', alpha=0.5))

                if not neg_shifts.empty:
                    plt.boxplot(neg_shifts[cols].values, positions=np.array(range(len(cols)))*2+0.4, 
                            widths=0.6, labels=[''] * len(cols), patch_artist=True,
                            boxprops=dict(facecolor='red', alpha=0.5))

                plt.axhline(y=0, color='gray', linestyle='--')
                plt.title(f'Randamente după schimbări mari în sentiment pentru {ticker}')
                plt.ylabel('Randament (%)')
                plt.grid(True, alpha=0.3)

                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='green', alpha=0.5, label='După creștere sentiment'),
                    Patch(facecolor='red', alpha=0.5, label='După scădere sentiment')
                ]
                plt.legend(handles=legend_elements)
                plt.tight_layout()
                plt.show()

                print("\n=== Randamente medii după schimbări mari în sentiment ===")
                print("După creștere de sentiment:")
                print(pos_shifts[cols].mean())
                print("\nDupă scădere de sentiment:")
                print(neg_shifts[cols].mean())

        return {
            'correlation': correlation,
            'p_value': p_value,
            'lag_correlations': lag_correlations,
            'combined_df': combined_df
        }


if __name__ == "__main__":
    # Înlocuiește 'AAPL' cu ticker-ul companiei dorite și datele cu intervalul dorit
    ticker = 'GPC'
    start_date = '2025-04-01'
    end_date = '2025-04-30'

    # Dacă folosești date reale, asigură-te că ai o cheie API validă
    analyzer = EnhancedSentimentAnalyzer(api_key="d4f5d0badc134a1685e7a971c7ecbc49")

    # Obține știrile
    news_df = analyzer.get_news(ticker, start_date, end_date)
    if not news_df.empty:
        print("\nPrimele 5 rânduri din datele de știri:")
        print(news_df.head())

        # Analizează tendințele de sentiment
        sentiment_trends_df = analyzer.analyze_sentiment_trends(ticker, start_date, end_date)
        if not sentiment_trends_df.empty:
            print("\nPrimele 5 rânduri din tendințele de sentiment:")
            print(sentiment_trends_df.head())

            # Combină sentimentul cu prețul (acum ar trebui să funcționeze dacă create_prices_dataframe_of_company este implementată)
            combined_df = analyzer.combine_sentiment_with_price(ticker, start_date, end_date, None) # Sau o instanță a DB_CRUD dacă este necesar
            if combined_df is not None:
                print("\nPrimele 5 rânduri din datele combinate sentiment-preț:")
                print(combined_df.head())

                # Plotează analiza de sentiment
                analyzer.plot_sentiment_analysis(ticker, start_date, end_date, None) # Sau o instanță a DB_CRUD dacă este necesar

                # Analizează relația sentiment-preț
                combined_df_for_correlation = analyzer.analyze_sentiment_price_relationship(ticker, start_date, end_date, None) # Sau o instanță a DB_CRUD dacă este necesar