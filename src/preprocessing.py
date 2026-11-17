### Librerias ###
import pandas as pd
import numpy as np
from pathlib import Path


### 1. Cargar datos ###
print("--- 1. Cargando datos crudos ---")
ROOT_DIR = Path(__file__).resolve().parent.parent

df_mod860 = pd.read_csv(ROOT_DIR / 'data/raw/mod_860.csv')
df_mod861 = pd.read_csv(ROOT_DIR / 'data/raw/mod_861.csv', low_memory=False) #advertencia de tipos
df_mod862 = pd.read_csv(ROOT_DIR / 'data/raw/mod_862.csv', low_memory=False) #advertencia de tipos
df_mod863 = pd.read_csv(ROOT_DIR / 'data/raw/mod_863.csv')
df_mod864 = pd.read_csv(ROOT_DIR / 'data/raw/mod_864.csv')
print(f"Archivos cargados correctamente. Filas iniciales en mod_860: {len(df_mod860)}")


### 2. Juntar datos ###
print("\n--- 2. Uniendo modulos (Inner Join) ---")
ID = "ID_CARATULA"
  #Tres columnas son iguales, ID sirve de columna para join, las otras deben ser eliminadas
df_mod861 = df_mod861.drop(columns=["CUEST_NRO", "INTERNO_ID"])
df_mod862 = df_mod862.drop(columns=["CUEST_NRO", "INTERNO_ID"])
df_mod863 = df_mod863.drop(columns=["CUEST_NRO", "INTERNO_ID"])
df_mod864 = df_mod864.drop(columns=["CUEST_NRO", "INTERNO_ID"])

df = df_mod860
df = df.merge(df_mod861, on=ID, how="inner", validate="1:1") #INNER JOIN asegurandose que los IDs son unicos
df = df.merge(df_mod862, on=ID, how="inner", validate="1:1")
df = df.merge(df_mod863, on=ID, how="inner", validate="1:1")
df = df.merge(df_mod864, on=ID, how="inner", validate="1:1")

print(f"Dataset unido: {df.shape[0]} filas x {df.shape[1]} columnas")


### 3. Limpiar lineas malas ###
print("\n--- 3. Filtrando sentenciados y eliminando duplicados ---")
  #Limpiar personas no sentenciadas
n_total = len(df)
df = df[df["SITUACION_JURIDICA"] == "Sentenciado"]
print(f"Filtrado 'Sentenciado': {n_total - len(df)} filas eliminadas (quedan {len(df)})")

  #Limpiar duplicados
  #Dos personas diferentes no pueden coincidir en mas de cien características
df_sin_ids = df.drop(columns=['ID_CARATULA', 'INTERNO_ID', 'CUEST_NRO'], errors='ignore')
duplicados = df_sin_ids.duplicated(keep='first')
df = df[~duplicados].reset_index(drop=True)
print(f"Duplicados eliminados: {duplicados.sum()} filas (quedan {len(df)})")


### 4. Crear target ###
print("\n--- 4. Creando variable objetivo (TARGET) ---")
TARGET = "REINCIDENTE"
p219 = df["P219"].map({"Sí": True, "Si":True, "si":True, "No": False, "no":False}) #recidiva pena suspendida
p220 = df["P220"].map({"Sí": True, "Si":True, "si":True, "No": False, "no":False}) #recidiva pena efectiva
df[TARGET] = (p219 | p220).astype(int)

dist_target = df[TARGET].value_counts(normalize=True) * 100
print(f"Distribucion de {TARGET}: No (0) = {dist_target.get(0, 0):.2f}% | Si (1) = {dist_target.get(1, 0):.2f}%")


### 5. Renombrar y filtrar columnas ###
print("\n--- 5. Renombrando y seleccionando columnas ---")
df = df.rename(columns={
  "DI": "DISTRITO",
  "EST_PENIT": "PRISION",
  "E_CIVIL": "ESTADO_CIVIL",
  "INT_DD": "ULTIMO_DEPARTAMENTO",
  "DELITO_GENERICO": "DELITO",

  "P101": "LENGUA_MATERNA",
  "P103_1": "LEER?",
  "P103_2": "HABLAR?",
  "P103_3": "ESCRIBIR?",
  "P104_1": "NIVEL_EDUCATIVO",
  "P104_4_CCEE": "ESTUDIOS_ESTATAL?",

  "P107_8": "DEPRESION?",
  "P107_9": "ANSIEDAD?",
  "P107_10": "ADICCION_PSICOACTIVOS?",
  "P109_1": "DROGAS?",
  "P109A_1": "TIPO_DROGA",
  "P109_2": "ALCOHOL?",
  "P109A_2": "TIPO_ALCOHOL",
  "P114": "HA_TRABAJADO?",

  "P122": "EDAD_SIN_MAMA",
  "P123_5": "VIVIO_SIN_ADULTA_FEMININA?",
  "P124": "EDAD_SIN_PAPA",
  "P125_5": "VIVIO_SIN_ADULTO_MASCULINO?",
  "P126": "VIOLENCIA_FAMILIAR?",
  "P127": "PADRES_ALCOHOLICOS?",
  "P128": "PADRES_CONSUMAN_DROGA?",
  "P129": "PADRES_VIOLENCIA_CONYUGAL?",
  "P136": "BARRIO_DELICTIVO?",
  "P137": "HIJOS?",

  "P203": "MOTIVO",
  "P215": "INTERNO_JUVENIL?",
  "P303": "ESTUDIOS_PRISIONALES?",
  "P315": "VISITAS_FAMILIARES?"
})

columnas_filtradas = [
  "DISTRITO", "PRISION", "GENERO", "ESTADO_CIVIL", "RELIGION", "EDAD", "ULTIMO_DEPARTAMENTO",
  "DELITO",
  "LENGUA_MATERNA", "LEER?", "HABLAR?", "ESCRIBIR?", "NIVEL_EDUCATIVO", "ESTUDIOS_ESTATAL?",
  "DEPRESION?", "ANSIEDAD?", "ADICCION_PSICOACTIVOS?",
  "DROGAS?", "TIPO_DROGA", "ALCOHOL?", "TIPO_ALCOHOL",
  "HA_TRABAJADO?",
  "EDAD_SIN_MAMA", "VIVIO_SIN_ADULTA_FEMININA?", "EDAD_SIN_PAPA", "VIVIO_SIN_ADULTO_MASCULINO?",
  "VIOLENCIA_FAMILIAR?", "PADRES_ALCOHOLICOS?", "PADRES_CONSUMAN_DROGA?", "PADRES_VIOLENCIA_CONYUGAL?",
  "BARRIO_DELICTIVO?", "HIJOS?",
  "MOTIVO",
  "INTERNO_JUVENIL?",
  "ESTUDIOS_PRISIONALES?", "VISITAS_FAMILIARES?",
  TARGET
]

df = df[columnas_filtradas].copy()
print(f"Columnas seleccionadas: {df.shape[1]} (incluyendo {TARGET})")

### 6. Tratamiento especifico de sub columnas ###
print("\n--- 6. Imputando sub-preguntas condicionales ---")
df["TIPO_DROGA"] = df["TIPO_DROGA"].fillna("Ninguno")
df["TIPO_ALCOHOL"] = df["TIPO_ALCOHOL"].fillna("Ninguno")
df["VIVIO_SIN_ADULTA_FEMININA?"] = df["VIVIO_SIN_ADULTA_FEMININA?"].fillna("No")
df["VIVIO_SIN_ADULTO_MASCULINO?"] = df["VIVIO_SIN_ADULTO_MASCULINO?"].fillna("No")


### 7. Limpiar datos (codigos 98/99, outliers y NaNs) ###
print("\n--- 7. Limpiando codigos 98/99, outliers y filas con muchos NaN ---")
  #99 puede significar "No sabe / No especificado"
for col in df.columns:
    if df[col].dtype in ['int64', 'float64']:
        df.loc[df[col].isin([98, 99]), col] = np.nan
    elif df[col].dtype == 'object':
        df[col] = df[col].replace(['98', '99', '98.0', '99.0'], np.nan)

  #Valores atipicos reemplazadas por NaN
columns_num = ["EDAD", "EDAD_SIN_MAMA", "EDAD_SIN_PAPA"]
for c in columns_num:
    df[c] = pd.to_numeric(df[c], errors="coerce")
    q1 = df[c].quantile(0.25)
    q3 = df[c].quantile(0.75)
    iqr = q3 - q1
    min_limit = q1 - 3 * iqr
    max_limit = q3 + 3 * iqr
    atipicos_filtro = (df[c] < min_limit) | (df[c] > max_limit)
    print(f"Outliers convertidos a NaN en {c}: {atipicos_filtro.sum()} valores (rango valido: [{min_limit:.1f}, {max_limit:.1f}])")
    df.loc[atipicos_filtro, c] = np.nan

# --- VERIFICACIONES DE VALORES FALTANTES POR COLUMNAS Y LINEAS---
print("\nValores faltantes por columna:")
missing_by_col = df.isnull().sum()
missing_pct_col = (missing_by_col / len(df)) * 100
missing_df = pd.DataFrame({
    'Columna': missing_by_col.index,
    'Faltantes': missing_by_col.values,
    'Porcentaje (%)': missing_pct_col.values.round(2)
})
missing_df = missing_df[missing_df['Faltantes'] > 0].sort_values('Porcentaje (%)', ascending=False)

print(missing_df.to_string(index=False))

print("\nValores faltantes por fila:")
missing_by_row = df.isnull().sum(axis=1)
row_counts = missing_by_row.value_counts().sort_index()
fila_stats_df = pd.DataFrame({
    'Num Faltantes': row_counts.index,
    'Conteo Filas': row_counts.values,
    'Porcentaje (%)': ((row_counts.values / len(df)) * 100).round(2)
})
print(fila_stats_df.to_string(index=False))
print("-" * 65)
# ----------------------------------------------------------------

  #Borrar filas con mas de 20% de columnas NaN
LINEAS_NAN_LIMIT = 0.2
columns_nan_limit = np.ceil(LINEAS_NAN_LIMIT * len(columnas_filtradas)).astype(int)
n_before = df.shape[0]
df = df[df.isna().sum(axis=1) < columns_nan_limit].reset_index(drop=True)
n_after = df.shape[0]

print(f"Limite de columnas NaN por fila: {columns_nan_limit * 100:.0f}%")
print(f"Nombre de filas eliminadas: {n_before - n_after} (quedan {n_after} filas)")

  #Reemplazar los NaN por una columnas general o por la mediana
#"EDAD_SIN_PAPA" hacemos .median despues de train_test_split #16.34%
df["ULTIMO_DEPARTAMENTO"] = df["ULTIMO_DEPARTAMENTO"].fillna("Sin respuesta") #12.07%
#"EDAD_SIN_PAPA" hacemos .median despues de train_test_split #16.34% #16.34%
df["ESTUDIOS_ESTATAL?"] = df["ESTUDIOS_ESTATAL?"].fillna("Omisión") #5.22%
df["NIVEL_EDUCATIVO"] = df["NIVEL_EDUCATIVO"].fillna("Sin respuesta") #2.68%
df["VISITAS_FAMILIARES?"] = df["VISITAS_FAMILIARES?"].fillna("Otros") #0.11%
df["ESTUDIOS_PRISIONALES?"] = df["ESTUDIOS_PRISIONALES?"].fillna("Sin respuesta") #0.11%
df["INTERNO_JUVENIL?"] = df["INTERNO_JUVENIL?"].fillna("No sabe / No contesta") #0.09%
df["MOTIVO"] = df["MOTIVO"].fillna("Sin respuesta") #0.09%


### 8. Borrar columnas binarias con demasiado desbalance ###
print("\n--- 8. Evaluando desbalance en columnas binarias ---")
DESBALANCE_LIMIT = 0.98

def eliminarBinaryUnbalanced(data, target_col, desbalance_max=0.98):
    columnas_binarias = [
        c for c in data.columns
        if c != target_col and data[c].nunique(dropna=True) == 2
    ]
    
    columnas_a_borrar = []
    for c in columnas_binarias:
        prop = data[c].value_counts(normalize=True).iloc[0]
        if prop >= desbalance_max:
            columnas_a_borrar.append(c)
            
    print(f"Columnas binarias detectadas ({len(columnas_binarias)}): {columnas_binarias}")
    print(f"Columnas binarias eliminadas por desbalance >= {desbalance_max*100}%: {columnas_a_borrar}")
    
    return data.drop(columns=columnas_a_borrar)

df = eliminarBinaryUnbalanced(df, TARGET, DESBALANCE_LIMIT)


### 9. Agrupacion de categorias subrepresentadas ###
print("\n--- 9. Agrupando categorias raras (< 2%) en 'Otros' ---")
CATEGORY_CARDINAL_LIMIT = 0.02
category_columns = df.select_dtypes(include=["object", "category"]).columns #columnas categoricas

for col in category_columns:
    frequences = df[col].value_counts(normalize=True) #tab: "category", frequence
    rare_categories = frequences[frequences < CATEGORY_CARDINAL_LIMIT].index #nombres de los categorias raras
    if len(rare_categories) > 0:
        df[col] = df[col].replace(rare_categories, "Otros") #reemplazar los datos
        print(f"  - {col}: {len(rare_categories)} categorias agrupadas en 'Otros'")


### 10. One-Hot Encoding ###
print("\n--- 10. Aplicando One-Hot Encoding ---")
def oneHotEncoding(data):
    data_onehot = pd.get_dummies(data, drop_first=True)
    columnas_bool = data_onehot.select_dtypes(include=["bool"]).columns
    data_onehot[columnas_bool] = data_onehot[columnas_bool].astype(int)
    return data_onehot

df_onehot = oneHotEncoding(df)
print(f"Dimensiones tras One-Hot Encoding: {df_onehot.shape[0]} filas x {df_onehot.shape[1]} columnas")


### 11. Exportar dataset procesado ###
print("\n--- 11. Exportando dataset procesado ---")
version = "04"
output_path_onehot = ROOT_DIR / ("data/processed/dataset" + version + "_onehot.csv")
df_onehot.to_csv(output_path_onehot, index=False, encoding="utf-8")
print(f"Archivo guardado exitosamente en: {output_path_onehot}")
