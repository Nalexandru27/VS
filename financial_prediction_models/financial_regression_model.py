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

# 1. Configurarea parametrilor (Dacă vrei să-i ai centralizat)
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
]  # Toți metricii pentru DataFrame

# 2. Funcția principală de analiză și modelare
def main():
    # 3. Crearea DataFrame-ului
    df = create_financial_data_df()

    # 4. Preprocesarea datelor
    df = preprocess_data(df)

    # 5. Modelarea pentru fiecare metrică țintă
    for target_metric in METRICS_TO_PREDICT:
        print(f"\n--- Modelare pentru: {target_metric} ---")
        model_and_evaluate(df.copy(), target_metric)

# 6. Funcția pentru a crea DataFrame-ul
def create_financial_data_df():
    df = create_metrics_companies_dataframe(
        START_YEAR, END_YEAR, ALL_METRICS
    )  # Folosește parametrii constanți
    return df


# 7. Ingineria Caracteristicilor
def feature_engineering(df):
    """
    Adaugă caracteristici calculate (e.g., rate de creștere).
    """
    df = add_growth_rates(df, METRICS_TO_PREDICT, years_back=3)
    df = add_lagged_features(df, METRICS_TO_PREDICT, years_back=1)
    return df

def add_growth_rates(df, metrics, years_back=1):
    for metric in metrics:
        df[f'{metric}_growth'] = df.groupby('ticker')[metric].pct_change() * 100
    return df


def add_lagged_features(df, metrics, years_back=1):
    for metric in metrics:
        df[f'{metric}_lag_1'] = df.groupby('ticker')[metric].shift(years_back)
    return df


# 8. Funcția pentru preprocesarea datelor
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

# 8. Funcția pentru antrenarea și evaluarea modelelor
def model_and_evaluate(df, target_metric):
    # A. Pregătirea datelor
    X = df.drop(columns=[target_metric], errors='ignore')
    y = df[target_metric]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    # B. Antrenarea modelelor
    models = {
        'LinearRegression': LinearRegression(),
        'Ridge': Ridge(),
        'Lasso': Lasso(),
        'DecisionTreeRegressor': DecisionTreeRegressor(random_state=42),
        'RandomForestRegressor': RandomForestRegressor(random_state=42),
        'GradientBoostingRegressor': GradientBoostingRegressor(random_state=42)
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        results[name] = {'RMSE': rmse, 'R2': r2, 'y_true': y_test, 'y_pred': y_pred}    

        # Calculează rata de creștere a predicțiilor
        y_pred_series = pd.Series(y_pred, index=y_test.index)
        y_pred_growth = y_pred_series.pct_change() * 100
        results[name]['y_pred_growth'] = y_pred_growth

        # Calculează rata de creștere a valorilor reale
        y_true_growth = y_test.pct_change() * 100
        results[name]['y_true_growth'] = y_true_growth
    
    # C. Afișarea rezultatelor
    print(f"\nRezultate pentru {target_metric}:")
    for name, metrics in results.items():
        print(f"  {name}: RMSE = {metrics['RMSE']:.4f}, R^2 = {metrics['R2']:.4f}")

    # D. Validare încrucișată
    print("\nCross-Validation Scores:")
    for name, model in models.items():
        cv_scores_rmse = np.sqrt(-cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error'))
        cv_scores_r2 = cross_val_score(model, X, y, cv=5, scoring='r2')
        print(f"  {name}: CV RMSE = {cv_scores_rmse.mean():.4f} (+/- {cv_scores_rmse.std():.4f}), CV R^2 = {cv_scores_r2.mean():.4f} (+/- {cv_scores_r2.std():.4f}")

    # E. Vizualizarea
    visualize_predictions(y_test, results, target_metric)

def visualize_predictions(y_true, results, target_metric):
    plt.figure(figsize=(8, 6))
    for name, metrics in results.items():
        plt.scatter(y_true, metrics['y_pred'], label=name, alpha=0.7)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'k--', lw=2, label='Perfect')
    plt.xlabel('Real')
    plt.ylabel('Prezis')
    plt.title(f'Real vs. Prezis pentru {target_metric}')
    plt.legend()
    plt.grid(True)
    plt.show()

# 9. Apelarea funcției principale
if __name__ == "__main__":
    main()