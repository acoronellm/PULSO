"""Explicabilidad SHAP del modelo final de PULSO."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from ml.common import FEATURES, load_dataset, split_data


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT / "artifacts" / "final" / "model" / "pulso_xgboost.joblib"
DEFAULT_DATASET_PATH = ROOT / "data" / "processed" / "cardio_clean_v1.csv"
DEFAULT_CONFIG_PATH = ROOT / "ml" / "configs" / "final_model.yaml"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "shap"


def _require_shap():
    """Carga SHAP solo cuando se solicita una explicación."""
    try:
        import shap
    except ImportError as error:
        raise RuntimeError(
            "SHAP no está instalado. Instala las dependencias de "
            "requirements-ml.txt antes de generar explicaciones."
        ) from error
    return shap


def load_final_model(model_path: Path = DEFAULT_MODEL_PATH):
    """Carga y valida el pipeline final serializado."""
    if not model_path.exists():
        raise FileNotFoundError(
            f"No existe el modelo final en {model_path}. "
            "Reconstrúyelo con: python -m ml.final_evaluate "
            "--config ml/configs/final_model.yaml"
        )

    pipeline = joblib.load(model_path)
    steps = getattr(pipeline, "named_steps", {})
    if not {"preprocessor", "model"}.issubset(steps):
        raise ValueError(
            "El artefacto no tiene los pasos esperados: "
            "preprocessor y model."
        )

    model = steps["model"]
    if not hasattr(model, "get_booster"):
        raise TypeError("El modelo serializado no es un XGBClassifier.")

    return pipeline


def transform_for_shap(pipeline, X: pd.DataFrame):
    """Aplica el preprocesador entrenado y devuelve matriz y nombres."""
    missing = sorted(set(FEATURES) - set(X.columns))
    if missing:
        raise ValueError(f"Faltan características requeridas: {missing}")

    preprocessor = pipeline.named_steps["preprocessor"]
    transformed = preprocessor.transform(X[FEATURES])
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()

    feature_names = list(preprocessor.get_feature_names_out())
    return np.asarray(transformed), feature_names


def create_explainer(pipeline):
    """Crea TreeExplainer en escala raw compatible con XGBoost 3.x.

    La escala raw es el log-odds del modelo. La probabilidad se recupera
    aplicando la función sigmoide a la suma del valor base y SHAP.
    """
    shap = _require_shap()
    model = pipeline.named_steps["model"]
    return shap.TreeExplainer(
        model,
        feature_perturbation="tree_path_dependent",
        model_output="raw",
    )


def explain_pipeline(
    pipeline,
    X: pd.DataFrame,
):
    """Genera valores SHAP para un DataFrame con variables originales."""
    transformed, feature_names = transform_for_shap(pipeline, X)

    explainer = create_explainer(pipeline)
    explanation = explainer(transformed)
    explanation.feature_names = feature_names
    return explanation, feature_names


def global_importance(explanation, feature_names: list[str]) -> pd.DataFrame:
    """Calcula importancia media absoluta en escala raw (log-odds)."""
    values = np.asarray(explanation.values)
    if values.ndim == 3:
        values = values[:, :, 1]

    return (
        pd.DataFrame({
            "feature": feature_names,
            "mean_abs_shap": np.abs(values).mean(axis=0),
            "mean_shap": values.mean(axis=0),
        })
        .sort_values("mean_abs_shap", ascending=False)
        .reset_index(drop=True)
    )


def local_explanation(
    pipeline,
    X: pd.DataFrame,
    explanation,
    feature_names: list[str],
    threshold: float,
) -> pd.DataFrame:
    """Combina predicción, threshold y contribuciones de una muestra."""
    probabilities = pipeline.predict_proba(X[FEATURES])[:, 1]
    values = np.asarray(explanation.values)
    if values.ndim == 3:
        values = values[:, :, 1]

    rows = []
    for row_index, probability in enumerate(probabilities):
        for feature_index, feature_name in enumerate(feature_names):
            rows.append({
                "row": row_index,
                "probability": float(probability),
                "threshold": threshold,
                "prediction": int(probability >= threshold),
                "feature": feature_name,
                "shap_value": float(values[row_index, feature_index]),
                "shap_scale": "raw_log_odds",
            })
    return pd.DataFrame(rows)


def save_global_artifacts(
    explanation,
    feature_names: list[str],
    output_dir: Path,
):
    """Guarda tabla y visualizaciones de explicabilidad global."""
    shap = _require_shap()
    output_dir.mkdir(parents=True, exist_ok=True)

    importance = global_importance(explanation, feature_names)
    importance.to_csv(output_dir / "global_feature_importance.csv", index=False)

    shap.summary_plot(
        explanation,
        show=False,
        plot_type="bar",
    )
    plt.tight_layout()
    plt.savefig(output_dir / "shap_bar.png", bbox_inches="tight")
    plt.close()

    shap.summary_plot(explanation, show=False)
    plt.tight_layout()
    plt.savefig(output_dir / "shap_summary.png", bbox_inches="tight")
    plt.close()

    return importance


def _load_threshold(config_path: Path) -> float:
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    return float(config["threshold"])


def run_global_explanation(
    model_path: Path = DEFAULT_MODEL_PATH,
    dataset_path: Path = DEFAULT_DATASET_PATH,
    config_path: Path = DEFAULT_CONFIG_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    sample_size: int = 1000,
):
    """Genera explicaciones globales sobre una muestra del conjunto Test."""
    pipeline = load_final_model(model_path)
    X, y = load_dataset(dataset_path)
    (_, _), (_, _), (X_test, _) = split_data(X, y)

    if sample_size < 1:
        raise ValueError("sample_size debe ser positivo.")

    X_explain = X_test.sample(
        n=min(sample_size, len(X_test)),
        random_state=42,
    )

    explanation, feature_names = explain_pipeline(
        pipeline,
        X_explain,
    )
    importance = save_global_artifacts(
        explanation,
        feature_names,
        output_dir,
    )

    local = local_explanation(
        pipeline,
        X_explain.reset_index(drop=True),
        explanation,
        feature_names,
        threshold=_load_threshold(config_path),
    )
    local.to_csv(output_dir / "local_explanations.csv", index=False)
    return importance


def parse_args():
    parser = argparse.ArgumentParser(
        description="Genera explicaciones SHAP del modelo final de PULSO."
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sample-size", type=int, default=1000)
    return parser.parse_args()


def main():
    args = parse_args()
    importance = run_global_explanation(
        model_path=args.model,
        dataset_path=args.dataset,
        config_path=args.config,
        output_dir=args.output_dir,
        sample_size=args.sample_size,
    )
    print(importance.to_string(index=False))


if __name__ == "__main__":
    main()