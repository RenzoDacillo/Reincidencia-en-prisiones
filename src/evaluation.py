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
    classification_report
)


def evaluarModelo(modelo_info, X_test, X_test_scaled, y_test, umbral=0.5):
    """
    Calcula todas las metricas clave de clasificacion para un modelo entrenado.
    """
    modelo = modelo_info["model"]
    X_datos = X_test_scaled if modelo_info["requiere_escalado"] else X_test

    y_prob = modelo.predict_proba(X_datos)[:, 1]
    y_pred = (y_prob >= umbral).astype(int)

    metricas = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision (Reincidente)": precision_score(y_test, y_pred, zero_division=0),
        "Recall (Reincidente)": recall_score(y_test, y_pred, zero_division=0),
        "F1-Score (Reincidente)": f1_score(y_test, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, y_prob),
        "PR-AUC": average_precision_score(y_test, y_prob),
        "y_prob": y_prob,
        "y_pred": y_pred
    }
    return metricas


def compararModelos(modelos_dict, X_test, X_test_scaled, y_test, umbral=0.5):
    """
    Evalua multiples modelos y devuelve un DataFrame comparativo ordenado por ROC-AUC
    junto con las probabilidades y predicciones de cada modelo.
    """
    resultados = []
    predicciones = {}

    for nombre, info in modelos_dict.items():
        res = evaluarModelo(info, X_test, X_test_scaled, y_test, umbral=umbral)
        predicciones[nombre] = {
            "y_prob": res.pop("y_prob"),
            "y_pred": res.pop("y_pred")
        }
        res["Modelo"] = nombre
        resultados.append(res)

    df_resultados = pd.DataFrame(resultados).set_index("Modelo")
    df_resultados = df_resultados.sort_values(by="ROC-AUC", ascending=False)
    return df_resultados, predicciones


def encontrarMejorUmbral(y_test, y_prob):
    """
    Encuentra el umbral de probabilidad que maximiza el F1-Score de la clase positiva.
    """
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_prob)
    f1_scores = 2 * (precisions[:-1] * recalls[:-1]) / (precisions[:-1] + recalls[:-1] + 1e-10)
    idx_mejor = np.argmax(f1_scores)
    mejor_umbral = float(thresholds[idx_mejor])
    mejor_f1 = float(f1_scores[idx_mejor])
    return mejor_umbral, mejor_f1


def graficarMatricesConfusion(predicciones_dict, y_test):
    """
    Grafica las matrices de confusion de todos los modelos en una cuadricula.
    """
    n_modelos = len(predicciones_dict)
    cols = 2
    rows = int(np.ceil(n_modelos / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(12, 5 * rows))
    axes = np.array(axes).flatten()

    for idx, (nombre, preds) in enumerate(predicciones_dict.items()):
        cm = confusion_matrix(y_test, preds["y_pred"])
        disp = ConfusionMatrixDisplay(
            confusion_matrix=cm,
            display_labels=["No reincidente", "Reincidente"]
        )
        disp.plot(ax=axes[idx], colorbar=False, cmap="Blues")
        axes[idx].set_title(f"Matriz de Confusion - {nombre}")

    for idx in range(n_modelos, len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()
    plt.show()


def graficarCurvasROC_PR(predicciones_dict, y_test):
    """
    Grafica comparativamente las curvas ROC y Precision-Recall de los modelos.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    for nombre, preds in predicciones_dict.items():
        y_prob = preds["y_prob"]
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        auc_val = roc_auc_score(y_test, y_prob)
        ax1.plot(fpr, tpr, lw=2, label=f"{nombre} (AUC = {auc_val:.4f})")

        prec, rec, _ = precision_recall_curve(y_test, y_prob)
        ap_val = average_precision_score(y_test, y_prob)
        ax2.plot(rec, prec, lw=2, label=f"{nombre} (PR-AUC = {ap_val:.4f})")

    ax1.plot([0, 1], [0, 1], "k--", lw=1, label="Azar (AUC = 0.5000)")
    ax1.set_title("Curvas ROC Comparativas")
    ax1.set_xlabel("Tasa de Falsos Positivos (FPR)")
    ax1.set_ylabel("Tasa de Verdaderos Positivos (Recall)")
    ax1.legend(loc="lower right")
    ax1.grid(alpha=0.3)

    prevalencia = y_test.mean()
    ax2.axhline(prevalencia, color="k", linestyle="--", lw=1, label=f"Baseline ({prevalencia:.3f})")
    ax2.set_title("Curvas Precision-Recall Comparativas")
    ax2.set_xlabel("Recall (Sensibilidad)")
    ax2.set_ylabel("Precision")
    ax2.legend(loc="upper right")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def graficarImportanciaVariables(modelo_info, feature_names, nombre_modelo, top_n=20):
    """
    Grafica las top_n variables mas importantes de un modelo basado en arboles o lineal.
    """
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
        "Importancia": importancias
    }).sort_values(by="Importancia", ascending=False).head(top_n)

    plt.figure(figsize=(10, 7))
    sns.barplot(data=df_imp, x="Importancia", y="Variable", palette="viridis", hue="Variable", legend=False)
    plt.title(titulo)
    plt.xlabel("Importancia relativa")
    plt.ylabel("Caracteristica")
    plt.tight_layout()
    plt.show()

    return df_imp


def imprimirReporteDetallado(nombre_modelo, y_test, y_pred):
    """
    Imprime el reporte de clasificacion completo en consola.
    """
    print(f"=== Reporte de Clasificacion: {nombre_modelo} ===")
    print(classification_report(
        y_test,
        y_pred,
        target_names=["No reincidente (0)", "Reincidente (1)"]
    ))
    