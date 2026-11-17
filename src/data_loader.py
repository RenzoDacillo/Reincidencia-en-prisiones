### Como usar estas funciones ###

# import src.data_loader as data_loader
# X_train, X_test, y_train, y_test = data_loader.prepararDatos()
# X_train_scaled, X_test_scaled = data_loader.escalarDatos(X_train, X_test)

### Librerias ###
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


### Cargar y preparar datos ###
ROOT_DIR = Path(__file__).resolve().parent.parent
version = "04"
file_path = ROOT_DIR / ("data/processed/dataset" + version + "_onehot.csv")

TARGET = "REINCIDENTE"
COLS_NUMERICAS = ["EDAD", "EDAD_SIN_MAMA", "EDAD_SIN_PAPA"]

def prepararDatos(datos_csv=file_path, test_size=0.2, random_state=42):
    print(f"--- Cargando dataset version {version} ---")
    df = pd.read_csv(datos_csv)
    print(f"Dataset cargado: {df.shape[0]} filas x {df.shape[1]} columnas")

    # 1. Separar features y target
    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    # 2. Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    print(f"Split realizado (test_size={test_size}): Train = {len(X_train)} filas | Test = {len(X_test)} filas")

    # 3. Imputacion con la mediana (fit SOLO en X_train para evitar fuga de datos)
    ESM_median = X_train["EDAD_SIN_MAMA"].median()
    ESP_median = X_train["EDAD_SIN_PAPA"].median()
    X_train["EDAD_SIN_MAMA"] = X_train["EDAD_SIN_MAMA"].fillna(ESM_median)
    X_train["EDAD_SIN_PAPA"] = X_train["EDAD_SIN_PAPA"].fillna(ESP_median)
    X_test["EDAD_SIN_MAMA"] = X_test["EDAD_SIN_MAMA"].fillna(ESM_median)
    X_test["EDAD_SIN_PAPA"] = X_test["EDAD_SIN_PAPA"].fillna(ESP_median)

    # Verificacion final de seguridad
    nans_faltantes = X_train.isna().sum().sum() + X_test.isna().sum().sum()
    print(f"Total de NaN restantes en Train + Test: {nans_faltantes}")

    return X_train, X_test, y_train, y_test


def escalarDatos(X_train, X_test):
    #Sirve para Regresion Logistica, KNN y MLP
    cols_a_escalar = [c for c in COLS_NUMERICAS]
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    
    scaler = StandardScaler()
    X_train_scaled[cols_a_escalar] = scaler.fit_transform(X_train_scaled[cols_a_escalar])
    X_test_scaled[cols_a_escalar] = scaler.transform(X_test_scaled[cols_a_escalar])
    print(f"Escalado (StandardScaler) aplicado a: {cols_a_escalar}")
        
    return X_train_scaled, X_test_scaled
