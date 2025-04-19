# financial_regression_model.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, KFold, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from financial_predictor import create_metrics_companies_dataframe
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configurarea parametrilor
START_YEAR = 2018
END_YEAR = 2023
METRICS_TO_PREDICT = ['FCF_per_share', 'EPS', 'OperatingCF_per_share']
ALL_METRICS = [
    'MarketCap',
    'CurrentRatio',
    'DividendRecord',
    'DividendYield',
    'EPS',
    'FCF_per_share',
    'OperatingCF_per_share',
    'OperatingIncomeMargin',
    'ROE',
    'ROCE',
    'Debt_to_Total_Capital_Ratio',
    'NetIncome',
    'Revenue',
    'TotalAssets',
    'TotalLiabilities',
    'TotalEquity'
]  # Toți metricii pentru DataFrame

# Funcția principală de analiză și modelare
def main():
    # Crearea DataFrame-ului
    df = create_financial_data_df()

    # Ingineria Caracteristicilor
    df = feature_engineering(df)

    # Validarea modelului pe date istorice (opțional, dar recomandat)
    validation_results = validate_prediction_model(df.copy())

    if validation_results:
    # 1. Display detailed validation summary
        print("\n===== Validation Results Summary =====")
        for metric, results in validation_results.items():
            print(f"\nMetric: {metric}")
            print(f"  RMSE: {results['RMSE']:.4f}")
            print(f"  R^2: {results['R^2']:.4f}")
            print(f"  MAPE: {results['MAPE']:.2f}%")
        
        # 2. Create visualization comparing predicted vs actual values
        visualize_validation_results(validation_results)
        
        # 3. Save validation results to CSV files
        save_validation_results(validation_results)

     # 4. Use validation results to inform next_year predictions
    # (You could adjust model parameters based on validation performance)
    next_year_predictions = predict_next_year(df.copy(), next_year=2024, 
                                             validation_performance=validation_results)
    
    # Afișarea și salvarea rezultatelor
    print("\nPredicții pentru anul 2024:")
    for metric, data in next_year_predictions.items():
        print(f"\n{metric}:")
        print(f"  Media: {data['summary']['mean']:.4f}")
        print(f"  Mediana: {data['summary']['median']:.4f}")
        print(f"  Min: {data['summary']['min']:.4f}")
        print(f"  Max: {data['summary']['max']:.4f}")
        
        # Afișăm primele 5 predicții
        print("\n  Predicții pentru companii:")
        for i, (ticker, value) in enumerate(data['predictions'].items()):
            if i < 5:  # Afișăm doar primele 5
                print(f"    {ticker}: {value:.4f}")
            else:
                break
        
        # Salvăm predicțiile într-un CSV
        predictions_df = pd.DataFrame({
            'ticker': list(data['predictions'].keys()),
            f'{metric}_2024': list(data['predictions'].values())
        })
        predictions_df.to_csv(f'{metric}_2024_predictions.csv', index=False)
        print(f"  Predicțiile pentru {metric} au fost salvate în {metric}_2025_predictions.csv")
    
    # Analizăm și rezultatele modelului original (păstrat din codul original)
    # Preprocesarea datelor
    df_original = preprocess_data(df.copy())

    # Modelarea pentru fiecare metrică țintă (păstrat din codul original)
    fcf_results = predict_fcf(df_original.copy())
    eps_results = predict_eps(df_original.copy())
    opcf_results = predict_opCF(df_original.copy())

    # Vizualizarea și salvarea rezultatelor (păstrat din codul original)
    visualize_and_save_results(fcf_results, eps_results, opcf_results)

def visualize_validation_results(validation_results):
    """Create visualizations comparing predicted vs actual values from validation."""
    for metric, results in validation_results.items():
        true_values = list(results['true_values'].values())
        pred_values = list(results['predictions'].values())
        companies = list(results['true_values'].keys())
        
        # Create DataFrame for easier plotting
        df_plot = pd.DataFrame({
            'Company': companies,
            'Actual': true_values,
            'Predicted': pred_values,
            'Error %': [(p-t)/t*100 for p, t in zip(pred_values, true_values)]
        })
        
        # Create scatter plot of predicted vs actual
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=true_values, 
            y=pred_values, 
            mode='markers',
            marker=dict(size=8),
            text=companies,
            name='Predictions'
        ))
        
        # Add perfect prediction line
        min_val = min(min(true_values), min(pred_values))
        max_val = max(max(true_values), max(pred_values))
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            line=dict(color='black', dash='dash'),
            name='Perfect Prediction'
        ))
        
        fig.update_layout(
            title=f'Validation Results for {metric} (Year {2023})',
            xaxis_title='Actual Values',
            yaxis_title='Predicted Values',
            showlegend=True
        )
        
        fig.show()
        
        # Create bar chart of prediction errors
        df_plot = df_plot.sort_values(by='Error %', ascending=False)
        fig = px.bar(
            df_plot,
            x='Company',
            y='Error %',
            title=f'Prediction Error % for {metric}',
            color='Error %',
            color_continuous_scale='RdBu_r',
            range_color=[-50, 50]
        )
        fig.show()

def save_validation_results(validation_results):
    """Save validation results to CSV files."""
    for metric, results in validation_results.items():
        # Create DataFrame with validation results
        df_results = pd.DataFrame({
            'ticker': list(results['true_values'].keys()),
            f'{metric}_actual': list(results['true_values'].values()),
            f'{metric}_predicted': list(results['predictions'].values())
        })
        
        # Add error calculations
        df_results[f'{metric}_abs_error'] = abs(df_results[f'{metric}_predicted'] - df_results[f'{metric}_actual'])
        df_results[f'{metric}_pct_error'] = (df_results[f'{metric}_predicted'] - df_results[f'{metric}_actual']) / df_results[f'{metric}_actual'] * 100
        
        # Save to CSV
        filename = f'validation_{metric}_2023.csv'
        df_results.to_csv(filename, index=False)
        print(f"Validation results for {metric} saved to {filename}")

# Funcția pentru a crea DataFrame-ul
def create_financial_data_df():
    df = create_metrics_companies_dataframe(START_YEAR, END_YEAR, ALL_METRICS)
    return df

# Ingineria Caracteristicilor
def feature_engineering(df):
    """
    Adaugă caracteristici calculate (e.g., rate de creștere, rapoarte).
    """
    # Adaugă ratele de creștere pentru metricile țintă
    df = add_growth_rates(df, METRICS_TO_PREDICT, years_back=3)

    # Adaugă ratele de creștere pentru venituri și profit net
    df = add_growth_rates(df, ['Revenue', 'NetIncome'], years_back=3)

    df = add_lagged_features(df, METRICS_TO_PREDICT, years_back=1)
    df = add_financial_ratios(df)
    return df

def add_growth_rates(df, metrics, years_back=1):
    for metric in metrics:
        df[f'{metric}_growth'] = df.groupby('ticker')[metric].pct_change(fill_method=None) * 100
    return df


def add_lagged_features(df, metrics, years_back=1):
    for metric in metrics:
        df[f'{metric}_lag_1'] = df.groupby('ticker')[metric].shift(years_back)
    return df

def add_financial_ratios(df):
    df['Debt_to_Equity'] = df['TotalLiabilities'] / df['TotalEquity']
    df['Asset_Turnover'] = df['Revenue'] / df['TotalAssets']
    df['Profit_Margin'] = df['NetIncome'] / df['Revenue']
    return df

# Funcția pentru preprocesarea datelor
def preprocess_data(df):
    # A. Eliminarea coloanelor inutile
    df = df.drop(columns=['ticker', 'year'], errors='ignore')  # Excludem ticker și year

    # B. Gestionarea valorilor lipsă (Imputare)
    imputer = SimpleImputer(strategy='mean')
    df[df.select_dtypes(include=np.number).columns] = imputer.fit_transform(df[df.select_dtypes(include=np.number).columns])

    # C. Scalarea caracteristicilor
    scaler = StandardScaler()
    df[df.select_dtypes(include=np.number).columns] = scaler.fit_transform(df[df.select_dtypes(include=np.number).columns])

    return df

# Funcția pentru antrenarea și evaluarea modelelor
def model_and_evaluate(df, target_metric, model_type='all'):
    # A. Pregătirea datelor
    X = df.drop(columns=[target_metric], errors='ignore')
    y = df[target_metric]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if model_type == 'fcf':
        models = {'Ridge': Ridge()} # Modelul care a dat cele mai bune rezultate pentru FCF/share
    elif model_type == 'eps':
        models = {'DecisionTreeRegressor': DecisionTreeRegressor(random_state=42)}
    elif model_type == 'opCF':
        models = {'Ridge': Ridge()}
    else:
        models = {
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(),
            'Lasso': Lasso(),
            'DecisionTreeRegressor': DecisionTreeRegressor(random_state=42),
            'RandomForestRegressor': RandomForestRegressor(random_state=42),
            'GradientBoostingRegressor': GradientBoostingRegressor(random_state=42)
        }

    results = {
        'models': {},
        'y_true': y_test.tolist(),  # Adaugă valorile reale la nivelul principal
        'y_pred': {}  # Va stoca predicțiile pentru toate modelele
    }
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results['models'][name] = {'RMSE': rmse, 'R^2': r2}
        results['y_pred'][name] = y_pred.tolist()  # Stochează predicțiile pentru acest model

        # Calculează rata de creștere a predicțiilor
        y_pred_series = pd.Series(y_pred, index=y_test.index)
        y_pred_growth = y_pred_series.pct_change(fill_method=None) * 100
        results['models'][name]['y_pred_growth'] = y_pred_growth.tolist()

        # Calculează rata de creștere a valorilor reale (doar o dată)
        if 'y_true_growth' not in results:
            y_true_growth = y_test.pct_change(fill_method=None) * 100
            results['y_true_growth'] = y_true_growth.tolist()
    
    # C. Afișarea rezultatelor
    print(f"\nRezultate pentru {target_metric}:")
    for name, metrics in results['models'].items():
        print(f"  {name}: RMSE = {metrics['RMSE']:.4f}, R^2 = {metrics['R^2']:.4f}")

    # D. Validare încrucișată
    print("\nCross-Validation Scores:")
    for name, model in models.items():
        cv_scores_rmse = np.sqrt(-cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error'))
        cv_scores_r2 = cross_val_score(model, X, y, cv=5, scoring='r2')
        print(f"  {name}: CV RMSE = {cv_scores_rmse.mean():.4f} (+/- {cv_scores_rmse.std():.4f}), CV R^2 = {cv_scores_r2.mean():.4f} (+/- {cv_scores_r2.std():.4f})")

    # Stocăm y_test și y_pred doar pentru ultimul model (sau puteți alege modelul cu performanța cea mai bună)
    best_model = min(results['models'].items(), key=lambda x: x[1]['RMSE'])[0]
    results['best_model'] = best_model
    results['best_y_pred'] = results['y_pred'][best_model]

    return results

def visualize_predictions(results, target_metric):
    """Vizualizează predicțiile vs. valorile reale."""
    
    if not results or 'y_true' not in results:
        print(f"Nu există date valide pentru vizualizare pentru {target_metric}.")
        return

    y_true = pd.Series(results['y_true'])
    
    # Creem un subplot pentru fiecare model
    model_names = list(results['models'].keys())
    fig = make_subplots(rows=1, cols=len(model_names), subplot_titles=model_names)

    for i, name in enumerate(model_names, start=1):
        if name in results['y_pred']:
            y_pred = pd.Series(results['y_pred'][name])
            
            fig.add_trace(
                go.Scatter(x=y_true, y=y_pred, mode='markers', name=name, marker=dict(opacity=0.7)),
                row=1, col=i
            )
            
            # Adăugăm linia de referință pentru predicții perfecte
            min_val = min(y_true.min(), y_pred.min())
            max_val = max(y_true.max(), y_pred.max())
            fig.add_trace(
                go.Scatter(x=[min_val, max_val], y=[min_val, max_val], mode='lines', 
                          line=dict(color='black', dash='dash'), showlegend=(i==1), name='Perfect'),
                row=1, col=i
            )

    fig.update_layout(title_text=f'Real vs. Predicted for {target_metric}', showlegend=True)
    fig.update_xaxes(title_text='Real', row=1)
    fig.update_yaxes(title_text='Predicted', row=1)
    fig.show()

def predict_fcf(df, visualize=True):
    results = model_and_evaluate(df, 'FCF_per_share', model_type='fcf')
    if visualize:
        visualize_predictions(results, 'FCF_per_share')
    return results

def predict_eps(df, visualize=True):
    results = model_and_evaluate(df, 'EPS', model_type='eps')
    if visualize:
        visualize_predictions(results, 'EPS')
    return results

def predict_opCF(df, visualize=True):
    results = model_and_evaluate(df, 'OperatingCF_per_share', model_type='opCF')
    if visualize:
        visualize_predictions(results, 'OperatingCF_per_share')
    return results

def visualize_and_save_results(fcf_results, eps_results, opcf_results):
    """
    Vizualizează și salvează rezultatele predicțiilor.
    """
    # Verificăm dacă există rezultate (pentru a evita erori)
    if fcf_results is None or eps_results is None or opcf_results is None:
        print("Nu există rezultate valide pentru vizualizare și salvare.")
        return

    # 1. Crearea și salvarea DataFrames
    save_predictions_to_csv(fcf_results, 'fcf_predictions.csv')
    save_predictions_to_csv(eps_results, 'eps_predictions.csv')
    save_predictions_to_csv(opcf_results, 'opcf_predictions.csv')

    # 2. Vizualizarea (deja apelate în funcțiile predict_*)
    # Aceste apeluri sunt redundante, dar le păstrăm pentru claritate
    visualize_predictions(fcf_results, 'FCF_per_share')
    visualize_predictions(eps_results, 'EPS')
    visualize_predictions(opcf_results, 'OperatingCF_per_share')

def save_predictions_to_csv(results, filename):
    """
    Salvează valorile reale și prezise într-un fișier CSV.
    """
    if results is None or 'y_true' not in results or 'best_y_pred' not in results:
        print(f"Nu există rezultate complete pentru a salva în fișierul {filename}.")
        return

    try:
        df_to_save = pd.DataFrame({
            'Real': results['y_true'],
            f'Predicted_{results["best_model"]}': results['best_y_pred']
        })
        df_to_save.to_csv(filename, index=False)
        print(f"Rezultatele au fost salvate în fișierul {filename}")
    except Exception as e:
        print(f"Eroare la salvarea în fișierul {filename}: {e}")

def predict_next_year(df, target_metrics=['FCF_per_share', 'EPS', 'OperatingCF_per_share'], 
                      next_year=2024, validation_performance=None):
    """
    Predict financial values for next year, potentially adjusting based on validation performance.
    """
    results = {}
    
    # For each metric
    for metric in target_metrics:
        print(f"\nTraining model for {metric} prediction for year {next_year}...")
        
        # Select optimal model for each metric, potentially adjusting based on validation
        if validation_performance and metric in validation_performance:
            # Use validation performance to adjust parameters
            if validation_performance[metric]['MAPE'] > 30:
                print(f"  High validation error detected for {metric}. Using more conservative model.")
                # Use more conservative model setup when validation error is high
                if metric == 'FCF_per_share':
                    model = Ridge(alpha=2.0)  # Higher regularization
                elif metric == 'EPS':
                    model = DecisionTreeRegressor(max_depth=3, random_state=42)  # More restrictive depth
                elif metric == 'OperatingCF_per_share':
                    model = Ridge(alpha=2.0)
                else:
                    model = RandomForestRegressor(n_estimators=150, max_depth=5, random_state=42)
            else:
                # Use standard model setup when validation error is acceptable
                if metric == 'FCF_per_share':
                    model = Ridge(alpha=1.0)
                elif metric == 'EPS':
                    model = DecisionTreeRegressor(max_depth=5, random_state=42)
                elif metric == 'OperatingCF_per_share':
                    model = Ridge(alpha=1.0)
                else:
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            # Use standard model setup when no validation data is available
            # (original code)
            if metric == 'FCF_per_share':
                model = Ridge(alpha=1.0)
            elif metric == 'EPS':
                model = DecisionTreeRegressor(max_depth=5, random_state=42)
            elif metric == 'OperatingCF_per_share':
                model = Ridge(alpha=1.0)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Pregătim datele pentru antrenament (excludem ultimul an pentru validare)
        df_train = df.copy()
        
        # Adăugăm feature-uri avansate pentru a capta tendințele temporale
        df_train = add_temporal_features(df_train, metric)
        
        # Pregătim setul de date pentru intrarea următorului an
        next_year_data = prepare_next_year_input(df_train, next_year)
        
        # Extragem caracteristicile și ținta
        X = df_train.drop(columns=[metric, 'year', 'ticker'], errors='ignore')
        y = df_train[metric]
        
        # Standardizăm datele
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_scaled_df = pd.DataFrame(scaler.transform(X), columns=X.columns)
        
        # Antrenăm modelul pe toate datele disponibile
        model.fit(X_scaled_df, y)
        
        # Pregătim datele de intrare pentru anul viitor
        X_next = next_year_data.drop(columns=[metric, 'year', 'ticker'], errors='ignore')
        X_next_scaled = scaler.transform(X_next)  # Folosim același scaler pentru consistență
        
        # Facem predicția
        y_pred = model.predict(X_next_scaled)
        
        # Salvăm rezultatele într-un format util
        predictions_dict = {}
        for i, ticker in enumerate(next_year_data['ticker']):
            if i < len(y_pred):  # Pentru siguranță
                predictions_dict[ticker] = y_pred[i]
        
        results[metric] = {
            'predictions': predictions_dict,
            'summary': {
                'mean': np.mean(y_pred),
                'median': np.median(y_pred),
                'min': np.min(y_pred),
                'max': np.max(y_pred)
            }
        }
        
        # Evaluăm importanța caracteristicilor (pentru RandomForest și DecisionTree)
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_importance = dict(zip(X.columns, importances))
            results[metric]['feature_importance'] = feature_importance
    
    return results

def add_temporal_features(df, target_metric):
    """
    Adaugă caracteristici avansate pentru a capta tendințele temporale.
    """
    # Calculăm mai multe rate de creștere pe perioade diferite
    df[f'{target_metric}_growth_1y'] = df.groupby('ticker')[target_metric].pct_change(1, fill_method=None)
    df[f'{target_metric}_growth_2y'] = df.groupby('ticker')[target_metric].pct_change(2, fill_method=None) / 2  # Rată anualizată
    df[f'{target_metric}_growth_3y'] = df.groupby('ticker')[target_metric].pct_change(3, fill_method=None) / 3  # Rată anualizată
    
    # Calculăm medii mobile
    df[f'{target_metric}_ma_2y'] = df.groupby('ticker')[target_metric].rolling(window=2).mean().reset_index(level=0, drop=True)
    df[f'{target_metric}_ma_3y'] = df.groupby('ticker')[target_metric].rolling(window=3).mean().reset_index(level=0, drop=True)
    
    # Adăugăm volatilitatea (deviația standard)
    df[f'{target_metric}_volatility'] = df.groupby('ticker')[target_metric].rolling(window=3).std().reset_index(level=0, drop=True)
    
    # Adăugăm indicatori pentru tendințe
    df[f'{target_metric}_trend'] = df.groupby('ticker')[target_metric].diff() > 0
    df[f'{target_metric}_trend'] = df[f'{target_metric}_trend'].astype(int)
    
    # Adăugăm caracteristici pentru accelerarea creșterii
    df[f'{target_metric}_growth_accel'] = df.groupby('ticker')[f'{target_metric}_growth_1y'].diff()
        
    # Eliminăm valorile NaN rezultate din calculele de mai sus
    df = df.dropna()
    
    return df

def prepare_next_year_input(df, next_year):
    """
    Pregătește datele de intrare pentru predicția pentru anul următor.
    """
    # Selectăm datele din ultimul an disponibil pentru fiecare companie
    last_year_data = df.groupby('ticker').last().reset_index()
    
    # Copiem datele și actualizăm anul
    next_year_data = last_year_data.copy()
    next_year_data['year'] = next_year
    
    # Calculăm estimări pentru anumite valori pentru anul următor
    numeric_cols = next_year_data.select_dtypes(include=np.number).columns
    
    for col in numeric_cols:
        if col not in ['year']:
            # Calculăm rata medie de creștere pentru fiecare companie
            # Modificare aici - calculăm corect ratele de creștere
            growth_rates = {}
            for ticker in df['ticker'].unique():
                ticker_data = df[df['ticker'] == ticker][col]
                if len(ticker_data) >= 4:  # Verificăm dacă avem suficiente date
                    # Calculăm ultimele 3 rate de creștere
                    changes = ticker_data.pct_change(fill_method=None).dropna().tail(3)
                    if not changes.empty:
                        growth_rates[ticker] = changes.mean()
            
            # Aplicăm rata de creștere datelor din ultimul an
            for idx, row in next_year_data.iterrows():
                ticker = row['ticker']
                if ticker in growth_rates:
                    growth_rate = growth_rates[ticker]
                    # Limităm ratele extreme de creștere
                    growth_rate = max(min(growth_rate, 0.5), -0.3)  # Limităm între -30% și +50%
                    next_year_data.loc[idx, col] *= (1 + growth_rate)
    
    return next_year_data

# Funcție pentru a rula și evalua modelul pe date istorice
def validate_prediction_model(df, target_metrics=['FCF_per_share', 'EPS', 'OperatingCF_per_share'], validation_year=2023):
    """
    Validează modelul de predicție folosind date istorice cunoscute.
    Antrenează pe datele până în anul validation_year-1 și testează pe validation_year.
    """
    print(f"\nValidarea modelului de predicție folosind anul {validation_year} ca referință...")
    
    # Împărțim datele în set de antrenare (până în anul validation_year-1) și validare (validation_year)
    train_df = df[df['year'] < validation_year].copy()
    validation_df = df[df['year'] == validation_year].copy()
    
    # Dacă nu avem date de validare, nu putem valida
    if validation_df.empty:
        print(f"Nu există date pentru anul de validare {validation_year}.")
        return None
    
    validation_results = {}
    
    for metric in target_metrics:
        print(f"\nValidarea pentru {metric}...")
        
        # Adăugăm caracteristici temporale
        train_df_enhanced = add_temporal_features(train_df.copy(), metric)
        
        # Pregătim datele pentru anul de validare
        validation_input = prepare_next_year_input(train_df_enhanced, validation_year)
        
        # Selectăm modelul potrivit
        if metric == 'FCF_per_share':
            model = Ridge(alpha=1.0)
        elif metric == 'EPS':
            model = DecisionTreeRegressor(max_depth=5, random_state=42)
        elif metric == 'OperatingCF_per_share':
            model = Ridge(alpha=1.0)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Antrenăm modelul pe datele din trecut
        X_train = train_df_enhanced.drop(columns=[metric, 'year', 'ticker'], errors='ignore')
        y_train = train_df_enhanced[metric]
        
        # Standardizăm datele
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        model.fit(X_train_scaled, y_train)
        
        # Pregătim datele de intrare pentru validare
        X_val = validation_input.drop(columns=[metric, 'year', 'ticker'], errors='ignore')
        X_val_scaled = scaler.transform(X_val)
        
        # Facem predicția
        y_pred = model.predict(X_val_scaled)
        
        # Comparăm cu valorile reale
        validation_tickers = validation_input['ticker'].tolist()
        
        # Extragem valorile reale din setul de validare
        y_true = []
        for ticker in validation_tickers:
            true_value = validation_df[validation_df['ticker'] == ticker][metric].values
            if len(true_value) > 0:
                y_true.append(true_value[0])
            else:
                y_true.append(np.nan)
        
        # Calculăm metricile de performanță
        # Filtrăm valorile NaN
        valid_indices = [i for i, val in enumerate(y_true) if not np.isnan(val)]
        y_true_valid = [y_true[i] for i in valid_indices]
        y_pred_valid = [y_pred[i] for i in valid_indices]
        
        if len(y_true_valid) > 0:
            rmse = np.sqrt(mean_squared_error(y_true_valid, y_pred_valid))
            r2 = r2_score(y_true_valid, y_pred_valid)
            
            # Calculăm eroarea procentuală medie
            mape = np.mean(np.abs((np.array(y_true_valid) - np.array(y_pred_valid)) / np.array(y_true_valid))) * 100
            
            validation_results[metric] = {
                'RMSE': rmse,
                'R^2': r2,
                'MAPE': mape,
                'predictions': dict(zip([validation_tickers[i] for i in valid_indices], y_pred_valid)),
                'true_values': dict(zip([validation_tickers[i] for i in valid_indices], y_true_valid))
            }
            
            print(f"  {metric}: RMSE = {rmse:.4f}, R^2 = {r2:.4f}, MAPE = {mape:.2f}%")
            
            # Afișăm câteva exemple de predicții vs. valori reale
            print("\nExemple de predicții vs. valori reale:")
            for i in range(min(5, len(valid_indices))):
                ticker = validation_tickers[valid_indices[i]]
                print(f"  {ticker}: Predicție = {y_pred_valid[i]:.4f}, Real = {y_true_valid[i]:.4f}, Eroare = {((y_pred_valid[i] - y_true_valid[i])/y_true_valid[i]*100):.2f}%")
    
    return validation_results

# Apelarea funcției principale
if __name__ == "__main__":
    main()