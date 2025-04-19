# financial_regression_model.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer  # Pentru imputarea valorilor lipsă
from financial_predictor import create_metrics_companies_dataframe  # Importăm funcția

# 1. Configurarea parametrilor (Dacă vrei să-i ai centralizat)
START_YEAR = 2018
END_YEAR = 2022
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
        model_and_evaluate(df, target_metric)


# 6. Funcția pentru a crea DataFrame-ul
def create_financial_data_df():
    df = create_metrics_companies_dataframe(
        START_YEAR, END_YEAR, ALL_METRICS
    )  # Folosește parametrii constanți
    return df


# 7. Funcția pentru preprocesarea datelor
def preprocess_data(df):
    # A. Eliminarea coloanelor inutile
    df = df.drop(columns=['ticker', 'year'], errors='ignore')  # Excludem ticker și year

    # B. Gestionarea valorilor lipsă (Imputare)
    for col in df.columns:
        if df[col].dtype == 'float64':
            # Imputare cu media (poți schimba strategia)
            imputer = SimpleImputer(strategy='mean')
            df[col] = imputer.fit_transform(df[[col]])

    # C. Scalarea caracteristicilor (Important pentru unele modele)
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:  # Verifică dacă există coloane numerice
        scaler = StandardScaler()
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    return df


# 8. Funcția pentru antrenarea și evaluarea modelelor
def model_and_evaluate(df, target_metric):
    # A. Pregătirea datelor pentru modelare
    X = df.drop(
        columns=METRICS_TO_PREDICT, errors='ignore'
    )  # Caracteristici (toți metricii în afară de țintă)
    y = df[target_metric]  # Variabila țintă

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # B. Antrenarea modelelor
    models = {
        'LinearRegression': LinearRegression(),
        'Ridge': Ridge(alpha=1.0),  # Poți ajusta alpha
        'Lasso': Lasso(alpha=0.1),  # Poți ajusta alpha
        'DecisionTreeRegressor': DecisionTreeRegressor(max_depth=5),  # Poți ajusta max_depth
        'RandomForestRegressor': RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),  # Poți ajusta parametrii
        'GradientBoostingRegressor': GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42),  # Poți ajusta parametrii
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        results[name] = {'RMSE': rmse, 'R2': r2}

    # C. Afișarea rezultatelor
    print(f"\nRezultate pentru {target_metric}:")
    for name, metrics in results.items():
        print(f"  {name}: RMSE = {metrics['RMSE']:.4f}, R^2 = {metrics['R2']:.4f}")

    # D. (Opțional) Vizualizarea predicțiilor vs. valori reale
    # (Poți adăuga grafice aici)


# 9. Apelarea funcției principale
if __name__ == "__main__":
    main()