"""Comparación de calibración de modelos tuned."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import mlflow
import pandas as pd
import yaml

from sklearn.calibration import calibration_curve

from ml.calibration import (
    evaluate_probabilities,
    make_calibrated_model,
)
from ml.common import (
    load_dataset,
    make_pipeline,
    sha256_file,
    split_data,
)


ROOT = Path(__file__).resolve().parents[1]


def run_calibration(
    config_path: Path,
    data_path: Path,
):

    config = yaml.safe_load(
        config_path.read_text(
            encoding="utf-8"
        )
    )

    model_type = config["model_type"]

    X, y = load_dataset(data_path)

    (
        (X_train, y_train),
        (X_val, y_val),
        _,
    ) = split_data(X, y)

    base_pipeline = make_pipeline(config)

    # -----------------------------
    # 1. Modelo sin calibrar
    # -----------------------------

    base_pipeline.fit(
        X_train,
        y_train,
    )

    base_probabilities = (
        base_pipeline
        .predict_proba(X_val)[:, 1]
    )

    base_metrics = evaluate_probabilities(
        y_val,
        base_probabilities,
    )

    # -----------------------------
    # 2. Sigmoid
    # -----------------------------

    sigmoid_model = make_calibrated_model(
        base_pipeline,
        method="sigmoid",
        cv=5,
    )

    sigmoid_model.fit(
        X_train,
        y_train,
    )

    sigmoid_probabilities = (
        sigmoid_model
        .predict_proba(X_val)[:, 1]
    )

    sigmoid_metrics = evaluate_probabilities(
        y_val,
        sigmoid_probabilities,
    )

    # -----------------------------
    # 3. Isotonic
    # -----------------------------

    isotonic_model = make_calibrated_model(
        base_pipeline,
        method="isotonic",
        cv=5,
    )

    isotonic_model.fit(
        X_train,
        y_train,
    )

    isotonic_probabilities = (
        isotonic_model
        .predict_proba(X_val)[:, 1]
    )

    isotonic_metrics = evaluate_probabilities(
        y_val,
        isotonic_probabilities,
    )

    # -----------------------------
    # 4. Tabla comparativa
    # -----------------------------

    results = pd.DataFrame(
        [
            {
                "calibration": "uncalibrated",
                **base_metrics,
            },
            {
                "calibration": "sigmoid",
                **sigmoid_metrics,
            },
            {
                "calibration": "isotonic",
                **isotonic_metrics,
            },
        ]
    )

    results = results.sort_values(
        by=[
            "brier",
            "log_loss",
            "ece",
        ],
        ascending=True,
    )

    selected = results.iloc[0]

    print(
        "\nResultados de calibración:"
    )
    print(results)

    print(
        "\nCalibración seleccionada:"
    )
    print(selected)

    # -----------------------------
    # 5. Artefactos
    # -----------------------------

    output_dir = (
        ROOT
        / "artifacts"
        / "calibration"
        / model_type
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        output_dir
        / "calibration_results.csv"
    )

    results.to_csv(
        csv_path,
        index=False,
    )

    # -----------------------------
    # 6. Calibration curve
    # -----------------------------

    plt.figure()

    for name, probabilities in [
        (
            "uncalibrated",
            base_probabilities,
        ),
        (
            "sigmoid",
            sigmoid_probabilities,
        ),
        (
            "isotonic",
            isotonic_probabilities,
        ),
    ]:

        prob_true, prob_pred = (
            calibration_curve(
                y_val,
                probabilities,
                n_bins=10,
                strategy="uniform",
            )
        )

        plt.plot(
            prob_pred,
            prob_true,
            marker="o",
            label=name,
        )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="perfect",
    )

    plt.xlabel(
        "Mean predicted probability"
    )

    plt.ylabel(
        "Observed frequency"
    )

    plt.title(
        f"Calibration - {model_type}"
    )

    plt.legend()

    calibration_plot_path = (
        output_dir
        / "calibration_curve.png"
    )

    plt.savefig(
        calibration_plot_path,
        bbox_inches="tight",
    )

    plt.close()

    # -----------------------------
    # 7. MLflow
    # -----------------------------

    mlflow.set_tracking_uri(
        "sqlite:///mlflow.db"
    )

    mlflow.set_experiment(
        "PULSO-calibration"
    )

    with mlflow.start_run(
        run_name=(
            f"{model_type}_calibration"
        )
    ):

        mlflow.log_param(
            "model_type",
            model_type,
        )

        mlflow.log_param(
            "dataset_sha256",
            sha256_file(data_path),
        )

        mlflow.log_param(
            "calibration_cv",
            5,
        )

        mlflow.log_param(
            "selected_calibration",
            selected["calibration"],
        )

        for name, metrics in [
            (
                "uncalibrated",
                base_metrics,
            ),
            (
                "sigmoid",
                sigmoid_metrics,
            ),
            (
                "isotonic",
                isotonic_metrics,
            ),
        ]:

            for metric_name, value in (
                metrics.items()
            ):

                mlflow.log_metric(
                    f"{name}_{metric_name}",
                    value,
                )

        mlflow.log_artifact(
            str(csv_path),
            artifact_path="calibration",
        )

        mlflow.log_artifact(
            str(calibration_plot_path),
            artifact_path="calibration",
        )

        mlflow.log_artifact(
            str(config_path),
            artifact_path="config",
        )

    return selected, results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--data",
        type=Path,
        default=(
            ROOT
            / "data"
            / "processed"
            / "cardio_clean_v1.csv"
        ),
    )

    args = parser.parse_args()

    run_calibration(
        args.config.resolve(),
        args.data.resolve(),
    )


if __name__ == "__main__":
    main()