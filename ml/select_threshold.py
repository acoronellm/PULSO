from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from ml.common import (
    load_dataset,
    make_pipeline,
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

    # 4. Construir el modelo
    pipeline = make_pipeline(config)

    # 5. Entrenar SOLO con Train
    pipeline.fit(
        X_train,
        y_train
    )

    # 6. Obtener probabilidades SOLO sobre Validation
    probabilities = pipeline.predict_proba(
        X_val
    )[:, 1]

    # 7. Buscar threshold
    selected, results = search_threshold(
        y_val,
        probabilities,
        min_recall=0.80
    )

    print("\nThreshold seleccionado:")
    print(selected)

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