### Librerias ###
import pandas as pd
import numpy as np
from pathlib import Path


### Cargar datos ###
ROOT_DIR = Path(__file__).resolve().parent.parent

df_mod860 = pd.read_csv(ROOT_DIR / 'data/raw/mod_860.csv')
df_mod861 = pd.read_csv(ROOT_DIR / 'data/raw/mod_861.csv', low_memory=False) #advertencia de tipos
df_mod862 = pd.read_csv(ROOT_DIR / 'data/raw/mod_862.csv', low_memory=False)
df_mod863 = pd.read_csv(ROOT_DIR / 'data/raw/mod_863.csv')
df_mod864 = pd.read_csv(ROOT_DIR / 'data/raw/mod_864.csv')


### Juntar datos ###
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


### Limpiar lineas malas ###
  #Limpiar personas no sentenciadas
df = df[df["SITUACION_JURIDICA"] == "Sentenciado"]

  #Limpiar duplicados
  #Dos personas diferentes no pueden coincidir en mas de cien características
df_sin_ids = df.drop(['ID_CARATULA','INTERNO_ID','CUEST_NRO'], axis=1)
duplicados = df_sin_ids.duplicated(keep='first')

df = df[~duplicados]
df = df.reset_index(drop=True)


### Crear target ###
TARGET = "REINCIDENTE"
p219 = df["P219"].map({"Sí": True, "No": False}) #recidiva pena suspendida
p220 = df["P220"].map({"Sí": True, "No": False}) #recidiva pena efectiva
df[TARGET] = (p219 | p220).astype(int)


### Filtrar columnas ###
# columnas_filtradas = [
#     "ID_CARATULA", "DD", "DI" "EST_PENIT", "GENERO", "E_CIVIL", "RELIGION", "EDAD", "NACIONALIDAD", "INT_DD", "DELITO_GENERICO",
#     "P101", "P102", "P103_1", "P103_2", "P103_3", "P104_1", "P104_4_CCEE", "P105", "P107_8", "P107_9", "P107_10", "P109_1", "P109A_2", "P114", "P117", "P118", "P122", "P124", "P126", "P127", "P128", "P129", "P135", "P136", "P137",
#     "P201_DI", "P203", "P215",
#     "P303", "P315",
#     TARGET
# ]
columnas_filtradas = [
    "DI", "EST_PENIT", "GENERO", "E_CIVIL", "RELIGION", "EDAD", "NACIONALIDAD", "INT_DD", "DELITO_GENERICO",
    "P101", "P103_1", "P103_2", "P103_3", "P104_1", "P104_4_CCEE", "P107_8", "P107_9", "P107_10", "P109_1", "P114", "P122", "P124", "P126", "P127", "P128", "P129", "P136", "P137",
    "P203", "P215",
    "P303", "P315",
    TARGET
]
df = df[columnas_filtradas]


### Limpiar datos ###
  #99 puede significar "No sabe / No especificado"
columns99 = ["P122", "P124"]
for c in columns99:
  df[c] = pd.to_numeric(df[c], errors="coerce")
  df.loc[df[c] >= 98, c] = np.nan #reemplazado por NaN

  #Valores atipicos reemplazadas por NaN
columns_num = [c for c in df.select_dtypes("number") if c != TARGET]
for c in columns_num:
    q1 = df[c].quantile(0.25)
    q3 = df[c].quantile(0.75)
    iqr = q3 - q1
    min_limit = q1 - 3 * iqr
    max_limit = q3 + 3 * iqr
    df.loc[(df[c] < min_limit) | (df[c] > max_limit), c] = np.nan

#   #Verificaciones faltantes por columnas
# missing_by_col = df.isnull().sum()
# missing_pct_col = (missing_by_col / len(df)) * 100
# missing_df = pd.DataFrame({
#     'Columna': missing_by_col.index,
#     'Faltantes': missing_by_col.values,
#     'Porcentaje (%)': missing_pct_col.values
# })
# missing_df = missing_df[missing_df['Faltantes'] > 0].sort_values('Porcentaje (%)', ascending=False)
# missing_df

#   #Verificaciones faltantes por filas
# missing_by_row = df.isnull().sum(axis=1)
# fila_stats_df = pd.DataFrame({
#     'Num Faltantes': missing_by_row.value_counts().sort_index().index,
#     'Conteo Filas': missing_by_row.value_counts().sort_index().values
# })
# fila_stats_df

  #Borrar filas con mas de 20% de columnas NaN
columns_nan_limit = np.ceil(0.2 * len(columnas_filtradas)).astype(int)
n_before = df.shape[0]
df = df[df.isna().sum(axis=1) < columns_nan_limit]
n_after = df.shape[0]

#print(f"Limite de columnas NaN para borrar la fila: {columns_nan_limit}")
#print(f"Nombre de filas con mas de 20 porcientos de columnas NaN: {n_before - n_after}")

  #Reemplazar los NaN por una columnas general o por la mediana
    #!!!!!!!!!!!!! fuga de datos con .median !!!!!!!!!!! hacer lo despues de separar los datos
df["P124"] = df["P124"].fillna(df["P124"].median()) #16.34%
df["INT_DD"] = df["INT_DD"].fillna("Sin respuesta") #12.07%
df["P122"] = df["P122"].fillna(df["P122"].median()) #16.34%
df["P104_4_CCEE"] = df["P104_4_CCEE"].fillna("Omisión") #5.22%
df["P104_1"] = df["P104_1"].fillna("Sin respuesta") #2.68%
df["P315"] = df["P315"].fillna("Otros") #0.11%
df["P303"] = df["P303"].fillna("Sin respuesta") #0.11%
df["P215"] = df["P215"].fillna("No sabe / No contesta") #0.09%
df["P203"] = df["P203"].fillna("Sin respuesta") #0.09%


### Agrupacion de categorias subrepresentadas ###
category_cardinal_limit = 0.02  # 2%

category_columns = df.select_dtypes(include=["object", "category", "str"]).columns

for col in category_columns:
    frequences = df[col].value_counts(normalize=True) #tab: "category", frequence
    rare_categories = frequences[frequences < category_cardinal_limit].index #conservar el nombre de los categorias raras
    df[col] = df[col].replace(rare_categories, "Otros") #reemplazar los datos

### One-Hot Encoding ###
def oneHotEncoding(data):
  return pd.get_dummies(data, drop_first=True).astype(int)

df_onehot = oneHotEncoding(df)

### Exportar dataset procesado ###
version = "02"
output_path = ROOT_DIR / ("data/processed/dataset" + version + ".csv")
output_path_onehot = ROOT_DIR / ("data/processed/dataset" + version + "_onehot.csv")

df.to_csv(output_path, index=False, encoding="utf-8")
df.to_csv(output_path_onehot, index=False, encoding="utf-8")