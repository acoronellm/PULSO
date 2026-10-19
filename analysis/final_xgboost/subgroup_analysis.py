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


def load_final_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo final en: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def calculate_group_metrics(
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

    if len(np.unique(y_true)) == 2:
        roc_auc = roc_auc_score(
            y_true,
            probabilities,
        )
    else:
        roc_auc = np.nan

    prevalence = float(
        np.mean(y_true)
    )

    return {
        "n": len(y_true),
        "prevalence": prevalence,
        "accuracy": accuracy,
        "precision": precision,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "f1": f1,
        "roc_auc": roc_auc,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def evaluate_subgroup(
    X_test,
    y_test,
    probabilities,
    group_type,
    group_name,
    mask,
):
    y_group = y_test.loc[
        mask
    ]

    probabilities_group = probabilities[
        mask.to_numpy()
    ]

    metrics = calculate_group_metrics(
        y_group,
        probabilities_group,
    )

    return {
        "group_type": group_type,
        "group": group_name,
        **metrics,
    }


def analyze_subgroups(
    X_test,
    y_test,
    probabilities,
):
    results = []

    # -----------------------------------------------------
    # Sexo
    # -----------------------------------------------------

    for gender_value in [1, 2]:
        mask = (
            X_test["gender"]
            == gender_value
        )

        results.append(
            evaluate_subgroup(
                X_test,
                y_test,
                probabilities,
                group_type="gender",
                group_name=f"gender_{gender_value}",
                mask=mask,
            )
        )

    # -----------------------------------------------------
    # Edad
    # -----------------------------------------------------

    age_groups = [
        (
            "<50",
            X_test["age_years"] < 50,
        ),
        (
            "50-59",
            (
                (X_test["age_years"] >= 50)
                & (X_test["age_years"] < 60)
            ),
        ),
        (
            ">=60",
            X_test["age_years"] >= 60,
        ),
    ]

    for group_name, mask in age_groups:
        results.append(
            evaluate_subgroup(
                X_test,
                y_test,
                probabilities,
                group_type="age",
                group_name=group_name,
                mask=mask,
            )
        )

    return pd.DataFrame(results)


def main():
    print(
        "=== ANÁLISIS POR SUBGRUPOS ==="
    )
    print()

    df = load_and_clean_data()

    splits = create_splits(
        df
    )

    X_test, y_test = splits[
        "test"
    ]

    model = load_final_model()

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    subgroup_df = analyze_subgroups(
        X_test,
        y_test,
        probabilities,
    )

    output_path = (
        OUTPUT_DIR
        / "subgroup_metrics.csv"
    )

    subgroup_df.to_csv(
        output_path,
        index=False,
    )

    display_df = subgroup_df.copy()

    columns_to_format = [
        "prevalence",
        "accuracy",
        "precision",
        "sensitivity",
        "specificity",
        "f1",
        "roc_auc",
    ]

    for column in columns_to_format:
        display_df[column] = (
            display_df[column].map(
                lambda value: (
                    f"{value:.4f}"
                    if not pd.isna(value)
                    else "N/A"
                )
            )
        )

    print(
        display_df.to_string(
            index=False
        )
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