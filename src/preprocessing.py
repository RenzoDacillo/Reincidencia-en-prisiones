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
df_sin_ids = df.drop(columns=['ID_CARATULA', 'INTERNO_ID', 'CUEST_NRO'], errors='ignore')
duplicados = df_sin_ids.duplicated(keep='first')

df = df[~duplicados]
df = df.reset_index(drop=True)


### Crear target ###
TARGET = "REINCIDENTE"
p219 = df["P219"].map({"Sí": True, "Si":True, "si":True, "No": False, "no":False}) #recidiva pena suspendida
p220 = df["P220"].map({"Sí": True, "Si":True, "si":True, "No": False, "no":False}) #recidiva pena efectiva
df[TARGET] = (p219 | p220).astype(int)


### Renombrar columnas ###
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

### Filtrar columnas ###
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
columnas_filtradas_con_desbalances = [
  "LENGUA_MATERNA", "LEER?", "HABLAR?", "ESCRIBIR?",
  "ESTUDIOS_ESTATAL?", "DEPRESION?", "ANSIEDAD?", "ADICCION_PSICOACTIVOS?",
  "HA_TRABAJADO?", "TIPO_ALCOHOL", "VIVIO_SIN_ADULTA_FEMININA?", "VIVIO_SIN_ADULTO_MASCULINO?",
  "PADRES_CONSUMAN_DROGA?"
]
columnas_filtradas_sin_desbalances = [ # Creamos dos datasets
    col for col in columnas_filtradas
    if col not in columnas_filtradas_con_desbalances
]
df = df[columnas_filtradas]


### Tratamiento especifico de sub columnas ###
df["TIPO_DROGA"] = df["TIPO_DROGA"].fillna("Ninguno")
df["TIPO_ALCOHOL"] = df["TIPO_ALCOHOL"].fillna("Ninguno")
df["VIVIO_SIN_ADULTA_FEMININA?"] = df["VIVIO_SIN_ADULTA_FEMININA?"].fillna("No")
df["VIVIO_SIN_ADULTO_MASCULINO?"] = df["VIVIO_SIN_ADULTO_MASCULINO?"].fillna("No")

### Limpiar datos ###
  #99 puede significar "No sabe / No especificado"
#columns99 = ["EDAD_SIN_MAMA", "EDAD_SIN_PAPA"]
#for c in columns99:
#  df[c] = pd.to_numeric(df[c], errors="coerce")
#  df.loc[df[c] >= 98, c] = np.nan #reemplazado por NaN

for col in df.columns:
    if df[col].dtype in ['int64', 'float64']:
        df.loc[df[col].isin([98, 99]), col] = np.nan
    elif df[col].dtype == 'object':
        df[col] = df[col].replace(['98', '99', '98.0', '99.0'], np.nan)

  #Valores atipicos reemplazadas por NaN
columns_num = ["EDAD"]
for c in columns_num:
    df[c] = pd.to_numeric(df[c], errors="coerce")
    q1 = df[c].quantile(0.25)
    q3 = df[c].quantile(0.75)
    iqr = q3 - q1
    min_limit = q1 - 3 * iqr
    max_limit = q3 + 3 * iqr
    df.loc[(df[c] < min_limit) | (df[c] > max_limit), c] = np.nan


############################
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
############################

  #Borrar filas con mas de 20% de columnas NaN
columns_nan_limit = np.ceil(0.2 * len(columnas_filtradas)).astype(int)
n_before = df.shape[0]
df = df[df.isna().sum(axis=1) < columns_nan_limit]
n_after = df.shape[0]

#print(f"Limite de columnas NaN para borrar la fila: {columns_nan_limit}")
#print(f"Nombre de filas con mas de 20 porcientos de columnas NaN: {n_before - n_after}")

  #Reemplazar los NaN por una columnas general o por la mediana
    #!!!!!!!!!!!!! fuga de datos con .median !!!!!!!!!!! hacer lo despues de separar los datos
df["EDAD_SIN_PAPA"] = df["EDAD_SIN_PAPA"].fillna(df["EDAD_SIN_PAPA"].median()) #16.34%
df["ULTIMO_DEPARTAMENTO"] = df["ULTIMO_DEPARTAMENTO"].fillna("Sin respuesta") #12.07%
df["EDAD_SIN_MAMA"] = df["EDAD_SIN_MAMA"].fillna(df["EDAD_SIN_MAMA"].median()) #16.34%
df["ESTUDIOS_ESTATAL?"] = df["ESTUDIOS_ESTATAL?"].fillna("Omisión") #5.22%
df["NIVEL_EDUCATIVO"] = df["NIVEL_EDUCATIVO"].fillna("Sin respuesta") #2.68%
df["VISITAS_FAMILIARES?"] = df["VISITAS_FAMILIARES?"].fillna("Otros") #0.11%
df["ESTUDIOS_PRISIONALES?"] = df["ESTUDIOS_PRISIONALES?"].fillna("Sin respuesta") #0.11%
df["INTERNO_JUVENIL?"] = df["INTERNO_JUVENIL?"].fillna("No sabe / No contesta") #0.09%
df["MOTIVO"] = df["MOTIVO"].fillna("Sin respuesta") #0.09%


### Agrupacion de categorias subrepresentadas ###
category_cardinal_limit = 0.02  # 2%

category_columns = df.select_dtypes(include=["object", "category"]).columns #columnas categoricas

for col in category_columns:
  frequences = df[col].value_counts(normalize=True) #tab: "category", frequence
  rare_categories = frequences[frequences < category_cardinal_limit].index #nombres de los categorias raras
  df[col] = df[col].replace(rare_categories, "Otros") #reemplazar los datos


### One-Hot Encoding ###
def oneHotEncoding(data):
  return pd.get_dummies(data, drop_first=True).astype(int)

df_onehot = oneHotEncoding(df)

df_sin_desbalances = df[columnas_filtradas_sin_desbalances]

### Exportar dataset procesado ###
version = "03"
output_path = ROOT_DIR / ("data/processed/dataset" + version + ".csv")
output_path_onehot = ROOT_DIR / ("data/processed/dataset" + version + "_onehot.csv")
output_path_sin_desbalances = ROOT_DIR / ("data/processed/dataset" + version + "_sin_desbalances.csv")

df.to_csv(output_path, index=False, encoding="utf-8")
df_onehot.to_csv(output_path_onehot, index=False, encoding="utf-8")
df_sin_desbalances.to_csv(output_path_sin_desbalances, index=False, encoding="utf-8")