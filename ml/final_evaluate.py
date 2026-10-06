from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import mlflow
import pandas as pd
import yaml

from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from ml.calibration import (
    expected_calibration_error,
    make_calibrated_model,
)

from ml.common import (
    load_dataset,
    make_pipeline,
    sha256_file,
    split_data,
)


ROOT = Path(__file__).resolve().parents[1]


def calculate_final_metrics(
    y_true,
    probabilities,
    predictions,
):
    """
    Calcula las métricas finales del modelo sobre Test.
    """

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    specificity = (
        tn / (tn + fp)
        if (tn + fp) > 0
        else 0.0
    )

    metrics = {
        "accuracy": float(
            accuracy_score(
                y_true,
                predictions,
            )
        ),
        "precision": float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "specificity": float(
            specificity
        ),
        "f1": float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),
        "brier": float(
            brier_score_loss(
                y_true,
                probabilities,
            )
        ),
        "log_loss": float(
            log_loss(
                y_true,
                probabilities,
            )
        ),
        "ece": float(
            expected_calibration_error(
                y_true,
                probabilities,
                n_bins=10,
            )
        ),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }

    return metrics


def save_confusion_matrix(
    y_true,
    predictions,
    output_path: Path,
):
    """
    Guarda la matriz de confusión del conjunto Test.
    """

    cm = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    )

    fig, ax = plt.subplots()

    image = ax.imshow(cm)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])

    ax.set_xticklabels([
        "Predicted 0",
        "Predicted 1",
    ])

    ax.set_yticklabels([
        "Actual 0",
        "Actual 1",
    ])

    ax.set_xlabel(
        "Predicted label"
    )

    ax.set_ylabel(
        "True label"
    )

    ax.set_title(
        "Final Test Confusion Matrix"
    )

    for i in range(2):
        for j in range(2):

            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
            )

    fig.colorbar(
        image,
        ax=ax,
    )

    plt.savefig(
        output_path,
        bbox_inches="tight",
    )

    plt.close()


def save_roc_curve(
    y_true,
    probabilities,
    output_path: Path,
):
    """
    Guarda la curva ROC del conjunto Test.
    """

    fpr, tpr, _ = roc_curve(
        y_true,
        probabilities,
    )

    auc = roc_auc_score(
        y_true,
        probabilities,
    )

    plt.figure()

    plt.plot(
        fpr,
        tpr,
        label=f"ROC-AUC = {auc:.4f}",
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Random classifier",
    )

    plt.xlabel(
        "False Positive Rate"
    )

    plt.ylabel(
        "True Positive Rate"
    )

    plt.title(
        "Final Test ROC Curve"
    )

    plt.legend()

    plt.savefig(
        output_path,
        bbox_inches="tight",
    )

    plt.close()


def save_precision_recall_curve(
    y_true,
    probabilities,
    output_path: Path,
):
    """
    Guarda la curva Precision-Recall del conjunto Test.
    """

    precision, recall, _ = (
        precision_recall_curve(
            y_true,
            probabilities,
        )
    )

    plt.figure()

    plt.plot(
        recall,
        precision,
    )

    plt.xlabel(
        "Recall"
    )

    plt.ylabel(
        "Precision"
    )

    plt.title(
        "Final Test Precision-Recall Curve"
    )

    plt.savefig(
        output_path,
        bbox_inches="tight",
    )

    plt.close()


def save_calibration_curve(
    y_true,
    probabilities,
    output_path: Path,
):
    """
    Guarda la curva de calibración del conjunto Test.
    """

    prob_true, prob_pred = calibration_curve(
        y_true,
        probabilities,
        n_bins=10,
        strategy="uniform",
    )

    plt.figure()

    plt.plot(
        prob_pred,
        prob_true,
        marker="o",
        label="Final model",
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Perfect calibration",
    )

    plt.xlabel(
        "Mean predicted probability"
    )

    plt.ylabel(
        "Observed frequency"
    )

    plt.title(
        "Final Test Calibration Curve"
    )

    plt.legend()

    plt.savefig(
        output_path,
        bbox_inches="tight",
    )

    plt.close()


def build_final_model(
    config,
):
    """
    Construye el modelo final respetando la
    configuración de calibración congelada.
    """

    pipeline = make_pipeline(
        config
    )

    calibration_config = config.get(
        "calibration",
        {
            "method": "none",
        },
    )

    calibration_method = (
        calibration_config.get(
            "method",
            "none",
        )
    )

    if calibration_method == "none":

        return pipeline

    if calibration_method in {
        "sigmoid",
        "isotonic",
    }:

        calibration_cv = (
            calibration_config.get(
                "cv",
                5,
            )
        )

        return make_calibrated_model(
            pipeline,
            method=calibration_method,
            cv=calibration_cv,
        )

    raise ValueError(
        "Método de calibración "
        "no soportado: "
        f"{calibration_method}"
    )


def run_final_evaluation(
    config_path: Path,
    data_path: Path,
):
    """
    Ejecuta la evaluación final del candidato
    congelado sobre Test.

    Train y Validation se combinan para realizar
    el refit final.

    Test se utiliza únicamente para la evaluación
    final y no participa en selección de modelo,
    calibración ni threshold.
    """

    # -------------------------------------------------
    # 1. Cargar configuración final congelada
    # -------------------------------------------------

    config = yaml.safe_load(
        config_path.read_text(
            encoding="utf-8"
        )
    )

    model_type = config[
        "model_type"
    ]

    threshold = float(
        config[
            "threshold"
        ]
    )

    calibration_config = (
        config.get(
            "calibration",
            {
                "method": "none",
            },
        )
    )

    calibration_method = (
        calibration_config.get(
            "method",
            "none",
        )
    )

    # -------------------------------------------------
    # 2. Cargar dataset
    # -------------------------------------------------

    X, y = load_dataset(
        data_path
    )

    # -------------------------------------------------
    # 3. Reproducir split oficial
    # -------------------------------------------------

    (
        X_train,
        y_train,
    ), (
        X_val,
        y_val,
    ), (
        X_test,
        y_test,
    ) = split_data(
        X,
        y,
    )

    # -------------------------------------------------
    # 4. Combinar Train + Validation
    # -------------------------------------------------

    X_final_train = pd.concat(
        [
            X_train,
            X_val,
        ],
        axis=0,
    )

    y_final_train = pd.concat(
        [
            y_train,
            y_val,
        ],
        axis=0,
    )

    print(
        "\nFinal training distribution:"
    )

    print(
        f"Train original: {len(X_train)}"
    )

    print(
        f"Validation original: {len(X_val)}"
    )

    print(
        "Train + Validation: "
        f"{len(X_final_train)}"
    )

    print(
        f"Test: {len(X_test)}"
    )

    # -------------------------------------------------
    # 5. Construir modelo final
    # -------------------------------------------------

    model = build_final_model(
        config
    )

    # -------------------------------------------------
    # 6. Refit final SOLO con Train + Validation
    # -------------------------------------------------

    model.fit(
        X_final_train,
        y_final_train,
    )

    # -------------------------------------------------
    # 7. Probabilidades sobre Test
    # -------------------------------------------------

    probabilities = (
        model
        .predict_proba(
            X_test
        )[:, 1]
    )

    # -------------------------------------------------
    # 8. Aplicar threshold congelado
    # -------------------------------------------------

    predictions = (
        probabilities
        >= threshold
    ).astype(int)

    # -------------------------------------------------
    # 9. Calcular métricas finales
    # -------------------------------------------------

    metrics = calculate_final_metrics(
        y_test,
        probabilities,
        predictions,
    )

    print(
        "\nFinal Test Evaluation:"
    )

    print(
        f"Model: {model_type}"
    )

    print(
        "Calibration: "
        f"{calibration_method}"
    )

    print(
        f"Threshold: {threshold:.2f}"
    )

    print()

    for metric_name, value in (
        metrics.items()
    ):

        if metric_name in {
            "tn",
            "fp",
            "fn",
            "tp",
        }:

            print(
                f"{metric_name.upper()}: "
                f"{value}"
            )

        else:

            print(
                f"{metric_name}: "
                f"{value:.6f}"
            )

    # -------------------------------------------------
    # 10. Crear directorio de artefactos
    # -------------------------------------------------

    output_dir = (
        ROOT
        / "artifacts"
        / "final"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -------------------------------------------------
    # 11. Guardar métricas
    # -------------------------------------------------

    metrics_path = (
        output_dir
        / "test_metrics.csv"
    )

    metrics_df = pd.DataFrame(
        [
            {
                "model_type": model_type,
                "calibration": calibration_method,
                "threshold": threshold,
                **metrics,
            }
        ]
    )

    metrics_df.to_csv(
        metrics_path,
        index=False,
    )

    # -------------------------------------------------
    # 12. Guardar gráficos
    # -------------------------------------------------

    confusion_matrix_path = (
        output_dir
        / "confusion_matrix.png"
    )

    roc_curve_path = (
        output_dir
        / "roc_curve.png"
    )

    precision_recall_path = (
        output_dir
        / "precision_recall_curve.png"
    )

    calibration_curve_path = (
        output_dir
        / "calibration_curve.png"
    )

    save_confusion_matrix(
        y_test,
        predictions,
        confusion_matrix_path,
    )

    save_roc_curve(
        y_test,
        probabilities,
        roc_curve_path,
    )

    save_precision_recall_curve(
        y_test,
        probabilities,
        precision_recall_path,
    )

    save_calibration_curve(
        y_test,
        probabilities,
        calibration_curve_path,
    )

    # -------------------------------------------------
    # 13. Guardar modelo final
    # -------------------------------------------------

    model_dir = (
        output_dir
        / "model"
    )

    model_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
        model_dir
        / "pulso_xgboost.joblib"
    )

    joblib.dump(
        model,
        model_path,
    )

    # -------------------------------------------------
    # 14. Registrar en MLflow
    # -------------------------------------------------

    mlflow.set_tracking_uri(
        "sqlite:///mlflow.db"
    )

    mlflow.set_experiment(
        "PULSO-final-evaluation"
    )

    with mlflow.start_run(
        run_name=(
            f"{model_type}"
            "_final_test"
        )
    ):

        mlflow.log_param(
            "model_type",
            model_type,
        )

        mlflow.log_param(
            "threshold",
            threshold,
        )

        mlflow.log_param(
            "calibration_method",
            calibration_method,
        )

        mlflow.log_param(
            "refit_strategy",
            "train_plus_validation",
        )

        mlflow.log_param(
            "dataset_sha256",
            sha256_file(
                data_path
            ),
        )

        mlflow.log_param(
            "final_train_size",
            len(
                X_final_train
            ),
        )

        mlflow.log_param(
            "test_size",
            len(
                X_test
            ),
        )

        for metric_name, value in (
            metrics.items()
        ):

            mlflow.log_metric(
                f"test_{metric_name}",
                float(value),
            )

        mlflow.log_artifact(
            str(metrics_path),
            artifact_path="final",
        )

        mlflow.log_artifact(
            str(confusion_matrix_path),
            artifact_path="final",
        )

        mlflow.log_artifact(
            str(roc_curve_path),
            artifact_path="final",
        )

        mlflow.log_artifact(
            str(precision_recall_path),
            artifact_path="final",
        )

        mlflow.log_artifact(
            str(calibration_curve_path),
            artifact_path="final",
        )

        mlflow.log_artifact(
            str(config_path),
            artifact_path="config",
        )

        mlflow.log_artifact(
            str(model_path),
            artifact_path="model",
        )

    print(
        "\nArtefactos guardados en:"
    )

    print(
        output_dir
    )

    print(
        "\nModelo final guardado en:"
    )

    print(
        model_path
    )

    return (
        metrics,
        model,
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help=(
            "Configuración congelada "
            "del modelo final"
        ),
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

    run_final_evaluation(
        args.config.resolve(),
        args.data.resolve(),
    )


if __name__ == "__main__":
    main()