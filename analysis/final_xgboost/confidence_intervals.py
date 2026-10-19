from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
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

N_BOOTSTRAPS = 1000

RANDOM_STATE = 42

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
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo final en: "
            f"{MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


# ---------------------------------------------------------
# Métricas
# ---------------------------------------------------------

def calculate_metrics(
    y_true,
    probabilities,
):
    predictions = (
        probabilities >= THRESHOLD
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    accuracy = accuracy_score(
        y_true,
        predictions,
    )

    precision = precision_score(
        y_true,
        predictions,
        zero_division=0,
    )

    sensitivity = recall_score(
        y_true,
        predictions,
        zero_division=0,
    )

    specificity = (
        tn / (tn + fp)
        if (tn + fp) > 0
        else np.nan
    )

    f1 = f1_score(
        y_true,
        predictions,
        zero_division=0,
    )

    # ROC-AUC necesita ambas clases
    if len(np.unique(y_true)) == 2:
        roc_auc = roc_auc_score(
            y_true,
            probabilities,
        )
    else:
        roc_auc = np.nan

    return {
        "accuracy": accuracy,
        "precision": precision,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "f1": f1,
        "roc_auc": roc_auc,
    }


# ---------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------

def bootstrap_confidence_intervals(
    y_true,
    probabilities,
):
    """
    Calcula IC 95% mediante bootstrap percentil.

    En cada iteración se toma una muestra con reemplazo
    del conjunto test, conservando el mismo tamaño.
    """

    rng = np.random.default_rng(
        RANDOM_STATE
    )

    y_true = np.asarray(
        y_true
    )

    probabilities = np.asarray(
        probabilities
    )

    n = len(y_true)

    bootstrap_results = {
        "accuracy": [],
        "precision": [],
        "sensitivity": [],
        "specificity": [],
        "f1": [],
        "roc_auc": [],
    }

    for _ in range(
        N_BOOTSTRAPS
    ):
        indices = rng.integers(
            0,
            n,
            size=n,
        )

        y_sample = y_true[
            indices
        ]

        probabilities_sample = (
            probabilities[
                indices
            ]
        )

        metrics = calculate_metrics(
            y_sample,
            probabilities_sample,
        )

        for metric_name, value in metrics.items():
            if not np.isnan(value):
                bootstrap_results[
                    metric_name
                ].append(
                    value
                )

    return bootstrap_results


# ---------------------------------------------------------
# Construir tabla
# ---------------------------------------------------------

def build_ci_table(
    point_metrics,
    bootstrap_results,
):
    rows = []

    for metric_name in [
        "accuracy",
        "precision",
        "sensitivity",
        "specificity",
        "f1",
        "roc_auc",
    ]:

        values = np.asarray(
            bootstrap_results[
                metric_name
            ]
        )

        lower = np.percentile(
            values,
            2.5,
        )

        upper = np.percentile(
            values,
            97.5,
        )

        rows.append(
            {
                "metric": metric_name,
                "estimate": point_metrics[
                    metric_name
                ],
                "ci_95_lower": lower,
                "ci_95_upper": upper,
                "n_bootstrap_valid": len(
                    values
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print(
        "=== IC 95% XGBOOST FINAL EN TEST ==="
    )
    print()

    # Dataset y split
    df = load_and_clean_data()

    splits = create_splits(
        df
    )

    X_test, y_test = splits[
        "test"
    ]

    print(
        f"Tamaño test: "
        f"{len(y_test):,}"
    )

    print(
        f"Bootstrap iterations: "
        f"{N_BOOTSTRAPS:,}"
    )

    print()

    # Modelo
    model = load_final_model()

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    # Métricas puntuales
    point_metrics = calculate_metrics(
        y_test,
        probabilities,
    )

    # Bootstrap
    bootstrap_results = (
        bootstrap_confidence_intervals(
            y_test,
            probabilities,
        )
    )

    # Tabla final
    ci_df = build_ci_table(
        point_metrics,
        bootstrap_results,
    )

    output_path = (
        OUTPUT_DIR
        / "confidence_intervals.csv"
    )

    ci_df.to_csv(
        output_path,
        index=False,
    )

    print(
        "=== RESULTADOS ==="
    )
    print()

    for _, row in ci_df.iterrows():
        print(
            f"{row['metric']:<14} "
            f"{row['estimate']:.6f} "
            f"["
            f"{row['ci_95_lower']:.6f}, "
            f"{row['ci_95_upper']:.6f}"
            f"]"
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