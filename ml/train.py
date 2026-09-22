
"""Entrena UN baseline y registra la ejecución en MLflow; no accede a test."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

import joblib
import mlflow
import pandas as pd
import yaml
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ml.common import FEATURES, RANDOM_STATE, load_dataset, make_pipeline, sha256_file, split_data
from ml.evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "ml" / "configs"


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "not-available"


def run(config_path: Path, data_path: Path, tracking_uri: str | None = None) -> str:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not all(
        key in config for key in ("model_type", "model_params", "threshold")
    ):
        raise ValueError("Configuración incompleta")
    # Por defecto SQLite LOCAL. Un servidor compartido requiere URI explícita.
    mlflow.set_tracking_uri(tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
    mlflow.set_experiment("PULSO-cardio-baselines")
    X, y = load_dataset(data_path)
    (X_train, y_train), (X_val, y_val), _ = split_data(X, y)
    pipeline = make_pipeline(config)
    with mlflow.start_run(run_name=config["model_type"]) as active_run:
        mlflow.log_params({
            "model_type": config["model_type"],
            "threshold": config["threshold"],
            "dataset_sha256": sha256_file(data_path),
            "random_state": RANDOM_STATE,
            "train_rows": len(X_train), "validation_rows": len(X_val),
            **{f"model__{k}": v for k, v in config["model_params"].items()},
        })
        mlflow.set_tags({
            "git_commit": git_commit(),
            "dataset_path": str(data_path),
            "target": "cardio",
            "evaluation_split": "validation_only",
        })
        pipeline.fit(X_train, y_train)
        metrics = evaluate(pipeline, X_val, y_val, config["threshold"])
        mlflow.log_metrics(metrics)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            joblib.dump(pipeline, output / "pipeline.joblib")
            manifest = {
                "model_type": config["model_type"],
                "model_params": config["model_params"],
                "threshold": config["threshold"],
                "dataset_sha256": sha256_file(data_path),
                "git_commit": git_commit(),
                "features": FEATURES,
                "random_state": RANDOM_STATE,
                "test_set_used": False,
                "metrics_validation": metrics,
            }
            (output / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            (output / "config.yaml").write_text(
                config_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
            proba = pipeline.predict_proba(X_val)[:, list(pipeline.classes_).index(1)]
            pred = (proba >= config["threshold"]).astype(int)
            ConfusionMatrixDisplay.from_predictions(y_val, pred, labels=[0, 1])
            plt.savefig(output / "confusion_matrix.png", bbox_inches="tight")
            plt.close()
            RocCurveDisplay.from_predictions(y_val, proba)
            plt.savefig(output / "roc_curve.png", bbox_inches="tight")
            plt.close()
            names = pipeline.named_steps["preprocessor"].get_feature_names_out()
            estimator = pipeline.named_steps["model"]
            if config["model_type"] == "logistic_regression":
                pd.DataFrame({"feature": names, "coefficient": estimator.coef_[0]}).to_csv(
                    output / "coefficients.csv", index=False
                )
            else:
                pd.DataFrame({"feature": names, "importance": estimator.feature_importances_}).to_csv(
                    output / "feature_importances.csv", index=False
                )
                from sklearn.tree import plot_tree
                plt.figure(figsize=(22, 10))
                plot_tree(estimator, feature_names=names, class_names=["cardio=0", "cardio=1"],
                          filled=True, rounded=True, max_depth=3, fontsize=9)
                plt.savefig(output / "tree_first_levels.png", bbox_inches="tight")
                plt.close()
            mlflow.log_artifacts(str(output), artifact_path="candidate")
        print(json.dumps({"run_id": active_run.info.run_id, "validation": metrics}, indent=2))
        return active_run.info.run_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=ROOT / "data/processed/cardio_clean_v1.csv")
    parser.add_argument("--tracking-uri", default=None)
    args = parser.parse_args()
    run(args.config.resolve(), args.data.resolve(), args.tracking_uri)


if __name__ == "__main__":
    main()
