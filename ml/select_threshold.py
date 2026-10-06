from __future__ import annotations

import argparse
from pathlib import Path
import mlflow
import yaml

from ml.calibration import make_calibrated_model

from ml.common import (
    load_dataset,
    make_pipeline,
    sha256_file,
    split_data
)

from ml.threshold import search_threshold


ROOT = Path(__file__).resolve().parents[1]


def run_threshold_selection(
    config_path: Path,
    data_path: Path,
):
    # 1. Cargar configuración del modelo tuned
    config = yaml.safe_load(
        config_path.read_text(encoding="utf-8")
    )

    # 2. Cargar dataset depurado
    X, y = load_dataset(data_path)

    # 3. Mantener las mismas particiones
    (X_train, y_train), \
    (X_val, y_val), \
    _ = split_data(X, y)

    # 4. Construir modelo tuned base
    pipeline = make_pipeline(config)

    # 5. Revisar configuración de calibración
    calibration_config = config.get(
        "calibration",
        {
            "method": "none"
        }
    )

    calibration_method = calibration_config.get(
        "method",
        "none"
    )

    if calibration_method == "none":

        model = pipeline

    elif calibration_method in {
        "sigmoid",
        "isotonic",
    }:

        calibration_cv = calibration_config.get(
            "cv",
            5
        )

        model = make_calibrated_model(
            pipeline,
            method=calibration_method,
            cv=calibration_cv,
        )

    else:

        raise ValueError(
            "Método de calibración no soportado: "
            f"{calibration_method}"
        )


    # 6. Entrenar SOLO con Train
    model.fit(
        X_train,
        y_train
    )


    # 7. Obtener probabilidades SOLO sobre Validation
    probabilities = model.predict_proba(
        X_val
    )[:, 1]

    # 8. Buscar threshold
    selected, results = search_threshold(
        y_val,
        probabilities,
        min_recall=0.80
    )

    print("\nThreshold seleccionado:")
    print(selected)
    # 9. Guardar resultados completos en CSV
    output_dir = ROOT / "artifacts" / "threshold"
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    model_type = config["model_type"]

    csv_path = (
        output_dir
        / f"{model_type}_threshold_results.csv"
    )

    results.to_csv(
        csv_path,
        index=False
    )

    print(
        f"\nResultados guardados en: {csv_path}"
    )


    # 10. Registrar en MLflow
    mlflow.set_tracking_uri(
        "sqlite:///mlflow.db"
    )

    mlflow.set_experiment(
        "PULSO-threshold-selection"
    )

    with mlflow.start_run(
        run_name=f"{model_type}_threshold_selection"
    ):

        mlflow.log_param(
            "model_type",
            model_type
        )

        mlflow.log_param(
            "dataset_sha256",
            sha256_file(data_path)
        )
        mlflow.log_param(
            "calibration_method",
            calibration_method
        )

        if (
            calibration_method
            != "none"
        ):

            mlflow.log_param(
                "calibration_cv",
                calibration_config.get(
                    "cv",
                    5
                )
            )
        mlflow.log_param(
            "selected_threshold",
            float(selected["threshold"])
        )

        mlflow.log_param(
            "min_recall",
            0.80
        )

        mlflow.log_metric(
            "validation_accuracy",
            float(selected["accuracy"])
        )

        mlflow.log_metric(
            "validation_precision",
            float(selected["precision"])
        )

        mlflow.log_metric(
            "validation_recall",
            float(selected["recall"])
        )

        mlflow.log_metric(
            "validation_specificity",
            float(selected["specificity"])
        )

        mlflow.log_metric(
            "validation_f1",
            float(selected["f1"])
        )

        mlflow.log_artifact(
            str(csv_path),
            artifact_path="threshold"
        )

        mlflow.log_artifact(
            str(config_path),
            artifact_path="config"
        )
    return selected, results


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Configuración tuned del modelo"
    )

    parser.add_argument(
        "--data",
        type=Path,
        default=(
            ROOT
            / "data"
            / "processed"
            / "cardio_clean_v1.csv"
        )
    )

    args = parser.parse_args()

    run_threshold_selection(
        args.config.resolve(),
        args.data.resolve()
    )


if __name__ == "__main__":
    main()