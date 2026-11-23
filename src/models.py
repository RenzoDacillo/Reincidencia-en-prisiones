### Librerias ###
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"


def optimizarModelo(
    nombre_modelo,
    param_dist,
    X_train,
    X_train_scaled,
    y_train,
    n_iter=15,
    cv=5,
    random_state=42,
):
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)

    if nombre_modelo == "MLPClassifier":
        estimador = MLPClassifier(
            early_stopping=True,
            max_iter=300,
            random_state=random_state,
        )
        X_datos = X_train_scaled
        requiere_escalado = True

    elif nombre_modelo == "LogisticRegression":
        estimador = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=random_state,
        )
        X_datos = X_train_scaled
        requiere_escalado = True

    elif nombre_modelo == "RandomForest":
        estimador = RandomForestClassifier(
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=random_state,
        )
        X_datos = X_train
        requiere_escalado = False

    elif nombre_modelo == "KNN":
        estimador = KNeighborsClassifier(n_jobs=-1)
        X_datos = X_train_scaled
        requiere_escalado = True

    else:
        raise ValueError("Este modelo no existe")

    print(f"Optimizar {nombre_modelo}")
    search = RandomizedSearchCV(
        estimator=estimador,
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring="roc_auc",
        cv=skf,
        n_jobs=-1,
        random_state=random_state,
        verbose=1,
    )
    search.fit(X_datos, y_train)
    print(f"Mejor ROC-AUC CV ({nombre_modelo}): {search.best_score_:.4f}")
    print(f"Mejores parametros: {search.best_params_}\n")

    return {
        "model": search.best_estimator_,
        "best_params": search.best_params_,
        "best_cv_auc": search.best_score_,
        "requiere_escalado": requiere_escalado,
    }