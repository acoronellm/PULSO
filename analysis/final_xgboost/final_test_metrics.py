from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    brier_score_loss,
    log_loss,
    confusion_matrix,
)

from prevalence import (
    load_and_clean_data,
    create_splits,
)


# ---------------------------------------------------------
# Configuración
# ---------------------------------------------------------

THRESHOLD = 0.38

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "final"
    / "model"
    / "pulso_xgboost.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "analysis"
    / "final_xgboost"
    / "outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Modelo
# ---------------------------------------------------------

def load_final_model():
    """
    Carga el modelo final XGBoost de PULSO.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo final en: "
            f"{MODEL_PATH}"
        )

    model = joblib.load(
        MODEL_PATH
    )

    return model


# ---------------------------------------------------------
# Evaluación
# ---------------------------------------------------------

def evaluate_test_set(
    model,
    X_test,
    y_test,
):
    """
    Evalúa el modelo final exclusivamente sobre test.

    Las métricas de clasificación utilizan
    threshold = 0.38.

    ROC-AUC, Brier y Log Loss utilizan
    probabilidades.
    """

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    predictions = (
        probabilities >= THRESHOLD
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    ).ravel()

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    sensitivity = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    specificity = (
        tn / (tn + fp)
        if (tn + fp) > 0
        else 0.0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    brier = brier_score_loss(
        y_test,
        probabilities,
    )

    logloss = log_loss(
        y_test,
        probabilities,
    )

    metrics = {
        "n_test": len(y_test),
        "threshold": THRESHOLD,
        "accuracy": accuracy,
        "precision": precision,
        "sensitivity_recall": sensitivity,
        "specificity": specificity,
        "f1": f1,
        "roc_auc": roc_auc,
        "brier_score": brier,
        "log_loss": logloss,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }

    return metrics


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print(
        "=== EVALUACIÓN FINAL XGBOOST EN TEST ==="
    )
    print()

    # Dataset y splits
    df = load_and_clean_data()

    splits = create_splits(
        df
    )

    X_test, y_test = splits[
        "test"
    ]

    print(
        f"Tamaño del conjunto test: "
        f"{len(y_test):,}"
    )

    print(
        f"Prevalencia en test: "
        f"{y_test.mean() * 100:.2f}%"
    )

    print()

    # Modelo
    model = load_final_model()

    # Evaluación
    metrics = evaluate_test_set(
        model,
        X_test,
        y_test,
    )

    metrics_df = pd.DataFrame(
        [metrics]
    )

    output_path = (
        OUTPUT_DIR
        / "test_metrics.csv"
    )

    metrics_df.to_csv(
        output_path,
        index=False,
    )

    # -----------------------------------------------------
    # Mostrar resultados
    # -----------------------------------------------------

    print(
        "=== MÉTRICAS ==="
    )
    print()

    print(
        f"Threshold:    "
        f"{metrics['threshold']:.2f}"
    )

    print(
        f"Accuracy:     "
        f"{metrics['accuracy']:.6f}"
    )

    print(
        f"Precision:    "
        f"{metrics['precision']:.6f}"
    )

    print(
        f"Sensibilidad: "
        f"{metrics['sensitivity_recall']:.6f}"
    )

    print(
        f"Especificidad:"
        f" {metrics['specificity']:.6f}"
    )

    print(
        f"F1:           "
        f"{metrics['f1']:.6f}"
    )

    print(
        f"ROC-AUC:      "
        f"{metrics['roc_auc']:.6f}"
    )

    print(
        f"Brier:        "
        f"{metrics['brier_score']:.6f}"
    )

    print(
        f"Log Loss:     "
        f"{metrics['log_loss']:.6f}"
    )

    print()

    print(
        "=== MATRIZ DE CONFUSIÓN ==="
    )
    print()

    print(
        f"TN: {metrics['tn']}"
    )
    print(
        f"FP: {metrics['fp']}"
    )
    print(
        f"FN: {metrics['fn']}"
    )
    print(
        f"TP: {metrics['tp']}"
    )

    print()

    print(
        "Resultados guardados en:"
    )
    print(
        output_path
    )


if __name__ == "__main__":
    main()