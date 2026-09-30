"""Tuning de hiperparámetros mediante GridSearchCV."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import mlflow
import pandas as pd
import yaml

from sklearn.model_selection import (
    GridSearchCV,
    ParameterGrid,
)

from ml.common import (
    load_dataset,
    make_pipeline,
    sha256_file,
    split_data,
)

from contextlib import contextmanager

import joblib
from tqdm.auto import tqdm

ROOT = Path(__file__).resolve().parents[1]

@contextmanager
def tqdm_joblib(progress_bar):
    """
    Conecta la ejecución paralela de joblib con una barra tqdm.

    Permite visualizar:
    - número de fits completados;
    - porcentaje;
    - tiempo transcurrido;
    - velocidad;
    - ETA aproximada.
    """

    class TqdmBatchCompletionCallback(
        joblib.parallel.BatchCompletionCallBack
    ):
        def __call__(self, *args, **kwargs):
            progress_bar.update(
                n=self.batch_size
            )

            return super().__call__(
                *args,
                **kwargs
            )

    old_callback = (
        joblib.parallel.BatchCompletionCallBack
    )

    joblib.parallel.BatchCompletionCallBack = (
        TqdmBatchCompletionCallback
    )

    try:
        yield progress_bar

    finally:
        joblib.parallel.BatchCompletionCallBack = (
            old_callback
        )

        progress_bar.close()

def run_tuning(
    search_config_path: Path,
    base_config_path: Path,
    data_path: Path,
):
    search_config = yaml.safe_load(
        search_config_path.read_text(encoding="utf-8")
    )

    base_config = yaml.safe_load(
        base_config_path.read_text(encoding="utf-8")
    )

    X, y = load_dataset(data_path)

    (X_train, y_train), (_, _), (_, _) = split_data(X, y)

    pipeline = make_pipeline(base_config)

    param_grid = search_config["param_grid"]
    cv = search_config.get("cv", 5)

    n_candidates = len(
        list(
            ParameterGrid(param_grid)
        )
    )

    total_fits = n_candidates * cv

    print("\n=== GridSearchCV ===")
    print(
        f"Modelo: {search_config['model_type']}"
    )
    print(
        f"Configuraciones: {n_candidates}"
    )
    print(
        f"Folds: {cv}"
    )
    print(
        f"Entrenamientos totales: {total_fits}"
    )
    print("====================\n")
    grid = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring=search_config.get(
            "scoring",
            "roc_auc"
        ),
        cv=cv,
        n_jobs=-1,
        return_train_score=True,
        refit=True,
        verbose=0,
    )

    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("PULSO-model-tuning")

    with mlflow.start_run(
        run_name=f'{search_config["model_type"]}_gridsearch'
    ):

        start_time = time.time()

        with tqdm_joblib(
            tqdm(
                total=total_fits,
                desc=f"GridSearch {search_config['model_type']}",
                unit="fit",
                dynamic_ncols=True,
            )
        ):
            grid.fit(
                X_train,
                y_train
            )

        elapsed = time.time() - start_time
        mean_fit_time = (
            pd.Series(
                grid.cv_results_["mean_fit_time"]
            ).mean()
        )
        print("\nGridSearchCV completado.")
        print(
            f"Tiempo total: "
            f"{elapsed / 60:.2f} minutos"
        )
        print(
            f"Tiempo promedio por fit: "
            f"{mean_fit_time:.2f} segundos"
        )
        mlflow.log_param(
            "model_type",
            search_config["model_type"]
        )

        mlflow.log_param(
            "search_method",
            "GridSearchCV"
        )

        mlflow.log_param(
            "scoring",
            search_config.get("scoring", "roc_auc")
        )

        mlflow.log_param(
            "cv",
            search_config.get("cv", 5)
        )

        mlflow.log_param(
            "dataset_sha256",
            sha256_file(data_path)
        )

        mlflow.log_metric(
            "best_cv_score",
            grid.best_score_
        )
        mlflow.log_param(
            "n_candidates",
            n_candidates
        )

        mlflow.log_param(
            "total_fits",
            total_fits
        )

        mlflow.log_metric(
            "gridsearch_elapsed_seconds",
            elapsed
        )

        mlflow.log_metric(
            "mean_fit_time_seconds",
            mean_fit_time
        )
        for key, value in grid.best_params_.items():
            mlflow.log_param(
                f"best_{key}",
                value
            )

        results = pd.DataFrame(
            grid.cv_results_
        )

        output = ROOT / "artifacts" / "tuning"
        output.mkdir(
            parents=True,
            exist_ok=True
        )

        csv_path = (
            output
            / f'{search_config["model_type"]}_cv_results.csv'
        )

        results.to_csv(
            csv_path,
            index=False
        )

        mlflow.log_artifact(
            str(csv_path),
            artifact_path="gridsearch"
        )

        print("\nMejores parámetros:")
        print(
            json.dumps(
                grid.best_params_,
                indent=2,
                default=str
            )
        )

        print(
            "\nBest CV ROC-AUC:",
            round(grid.best_score_, 6)
        )

        return grid.best_params_


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--search-config",
        type=Path,
        required=True
    )

    parser.add_argument(
        "--base-config",
        type=Path,
        required=True
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

    run_tuning(
        args.search_config.resolve(),
        args.base_config.resolve(),
        args.data.resolve(),
    )


if __name__ == "__main__":
    main()
