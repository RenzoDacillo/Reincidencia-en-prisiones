### Librerias ###
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    precision_recall_curve,
    classification_report,
)

TRESHOLD = 0.5

def evaluarModelo(modelo_info, X_test, X_test_scaled, y_test):
    modelo = modelo_info["model"]
    X_datos = X_test_scaled if modelo_info["requiere_escalado"] else X_test

    y_prob = modelo.predict_proba(X_datos)[:, 1]
    y_pred = (y_prob >= TRESHOLD).astype(int)

    metricas = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision (Reincidente)": precision_score(y_test, y_pred, zero_division=0),
        "Recall (Reincidente)": recall_score(y_test, y_pred, zero_division=0),
        "F1-Score (Reincidente)": f1_score(y_test, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, y_prob),
        "PR-AUC": average_precision_score(y_test, y_prob),
        "y_prob": y_prob,
        "y_pred": y_pred,
    }
    return metricas


def compararModelos(modelos_dict, X_test, X_test_scaled, y_test):
    resultados = []
    predicciones = {}

    for nombre, info in modelos_dict.items():
        res = evaluarModelo(info, X_test, X_test_scaled, y_test)
        predicciones[nombre] = {
            "y_prob": res.pop("y_prob"),
            "y_pred": res.pop("y_pred"),
        }
        res["Modelo"] = nombre
        resultados.append(res)

    df_resultados = pd.DataFrame(resultados).set_index("Modelo")
    df_resultados = df_resultados.sort_values(by="ROC-AUC", ascending=False)
    return df_resultados, predicciones


def graficarMatricesConfusion(predicciones_dict, y_test):
    n_modelos = len(predicciones_dict)
    cols = 2
    rows = int(np.ceil(n_modelos / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(12, 5 * rows))
    axes = np.array(axes).flatten()

    for idx, (nombre, preds) in enumerate(predicciones_dict.items()):
        cm = confusion_matrix(y_test, preds["y_pred"])
        disp = ConfusionMatrixDisplay(
            confusion_matrix=cm,
            display_labels=["No reincidente", "Reincidente"],
        )
        disp.plot(ax=axes[idx], colorbar=False, cmap="Blues")
        axes[idx].set_title(f"Matriz de Confusion - {nombre}")

    for idx in range(n_modelos, len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()
    plt.show()


def graficarImportanciaVariables(modelo_info, feature_names, nombre_modelo, top_n=20):
    modelo = modelo_info["model"]

    if hasattr(modelo, "feature_importances_"):
        importancias = modelo.feature_importances_
        titulo = f"Top {top_n} Variables mas Importantes - {nombre_modelo}"
    elif hasattr(modelo, "coef_"):
        importancias = np.abs(modelo.coef_[0])
        titulo = f"Top {top_n} Coeficientes (|valor|) - {nombre_modelo}"
    else:
        print(f"El modelo {nombre_modelo} no expone importancia de variables directamente.")
        return None

    df_imp = pd.DataFrame({
        "Variable": feature_names,
        "Importancia": importancias,
    }).sort_values(by="Importancia", ascending=False).head(top_n)

    plt.figure(figsize=(10, 7))
    sns.barplot(
        data=df_imp,
        x="Importancia",
        y="Variable",
        palette="viridis",
        hue="Variable",
        legend=False,
    )
    plt.title(titulo)
    plt.xlabel("Importancia relativa")
    plt.ylabel("Caracteristica")
    plt.tight_layout()
    plt.show()

    return df_imp


def imprimirReporteDetallado(nombre_modelo, y_test, y_pred):
    print(classification_report(
        y_test,
        y_pred,
        target_names=["No reincidente (0)", "Reincidente (1)"],
    ))