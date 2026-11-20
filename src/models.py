### Librerias ###
import joblib
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"

def obtenerModelosBase(y_train, random_state=42):
    """
    Retorna un diccionario con los modelos base configurados para manejar
    el desbalanceo de clases (~16.5% reincidentes) sin fuga de datos.
    """
    desbalance = float(np.sum(y_train == 0) / np.sum(y_train == 1))

    modelos = {
        "LogisticRegression": {
            "estimator": LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=random_state
            ),
            "requiere_escalado": True
        },
        "RandomForest": {
            "estimator": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_leaf=5,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=random_state
            ),
            "requiere_escalado": False
        },
        "XGBoost": {
            "estimator": XGBClassifier(
                n_estimators=250,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=desbalance,
                eval_metric="logloss",
                n_jobs=-1,
                random_state=random_state
            ),
            "requiere_escalado": False
        },
        "LightGBM": {
            "estimator": LGBMClassifier(
                n_estimators=250,
                max_depth=8,
                learning_rate=0.05,
                num_leaves=31,
                subsample=0.8,
                colsample_bytree=0.8,
                class_weight="balanced",
                n_jobs=-1,
                verbose=-1,
                random_state=random_state
            ),
            "requiere_escalado": False
        }
    }
    return modelos


def entrenarModelosBase(X_train_simple, X_train_scaled, y_train, random_state=42):
    """
    Entrena todos los modelos base seleccionando automaticamente X_train_scaled
    para modelos lineales y X_train sin escalar para modelos basados en arboles.
    """
    modelos = obtenerModelosBase(y_train, random_state=random_state)

    for nombre, config in modelos.items():
        print(f"Entrenando modelo base: {nombre}...")
        X_train = X_train_scaled if config["requiere_escalado"] else X_train_simple
        config["estimator"].fit(X_train, y_train)

    return modelos


def optimizarModelo(nombre_modelo, X_train, X_train_scaled, y_train, n_iter=15, cv=5, random_state=42):
    """
    Optimiza hiperparametros de un modelo especifico mediante RandomizedSearchCV
    usando ROC-AUC como metrica principal y StratifiedKFold.
    """
    desbalance = float(np.sum(y_train == 0) / np.sum(y_train == 1))
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)

    if nombre_modelo == "LogisticRegression":
        estimador = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=random_state)
        param_dist = {
            "C": [0.001, 0.01, 0.1, 1.0, 10.0],
            "penalty": ["l2"],
            "solver": ["lbfgs", "saga"]
        }
        X_datos = X_train_scaled
        requiere_escalado = True

    elif nombre_modelo == "RandomForest":
        estimador = RandomForestClassifier(class_weight="balanced_subsample", n_jobs=-1, random_state=random_state)
        param_dist = {
            "n_estimators": [200, 300, 400],
            "max_depth": [10, 15, 20, None],
            "min_samples_split": [2, 5, 10],
            "min_samp   les_leaf": [2, 4, 8],
            "max_features": ["sqrt", "log2"]
        }
        X_datos = X_train
        requiere_escalado = False

    elif nombre_modelo == "XGBoost":
        estimador = XGBClassifier(
            scale_pos_weight=desbalance,
            eval_metric="logloss",
            n_jobs=-1,
            random_state=random_state
        )
        param_dist = {
            "n_estimators": [200, 300, 400],
            "max_depth": [4, 6, 8],
            "learning_rate": [0.01, 0.03, 0.05, 0.1],
            "subsample": [0.7, 0.8, 0.9],
            "colsample_bytree": [0.7, 0.8, 0.9],
            "min_child_weight": [1, 3, 5]
        }
        X_datos = X_train
        requiere_escalado = False

    elif nombre_modelo == "LightGBM":
        estimador = LGBMClassifier(
            class_weight="balanced",
            n_jobs=-1,
            verbose=-1,
            random_state=random_state
        )
        param_dist = {
            "n_estimators": [200, 300, 400],
            "max_depth": [6, 8, 12, -1],
            "learning_rate": [0.01, 0.03, 0.05, 0.1],
            "num_leaves": [15, 31, 63],
            "subsample": [0.7, 0.8, 0.9],
            "colsample_bytree": [0.7, 0.8, 0.9],
            "min_child_samples": [10, 20, 40]
        }
        X_datos = X_train
        requiere_escalado = False
    else:
        raise ValueError(f"Modelo '{nombre_modelo}' no soportado.")

    print(f"Optimizando {nombre_modelo} ({n_iter} iteraciones, {cv}-fold CV)...")
    search = RandomizedSearchCV(
        estimator=estimador,
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring="roc_auc",
        cv=skf,
        n_jobs=-1,
        random_state=random_state,
        verbose=1
    )
    search.fit(X_datos, y_train)
    print(f"Mejor ROC-AUC CV ({nombre_modelo}): {search.best_score_:.4f}")
    print(f"Mejores parametros: {search.best_params_}\n")

    return {
        "model": search.best_estimator_,
        "best_params": search.best_params_,
        "best_cv_auc": search.best_score_,
        "requiere_escalado": requiere_escalado
    }


def guardarModelo(modelo_dict, nombre_archivo):
    """
    Guarda el diccionario del modelo entrenado en la carpeta models/.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = MODELS_DIR / nombre_archivo
    f.dump(modelo_dict, ruta)
    print(f"Modelo guardado exitosamente en: {ruta}")
    return ruta
