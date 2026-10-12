from functools import lru_cache

import numpy as np
import pandas as pd
import shap

from .config import FEATURES
from .model_loader import load_model
from .schemas import (
    ExplanationResponse,
    PredictionRequest,
    ShapFactor,
)


@lru_cache(maxsize=1)
def get_explainer():
    """
    Crea y reutiliza el TreeExplainer del modelo final.
    """
    pipeline = load_model()

    model = pipeline.named_steps["model"]

    return shap.TreeExplainer(
        model,
        feature_perturbation="tree_path_dependent",
        model_output="raw",
    )


def _get_original_feature_name(
    transformed_name: str,
) -> str:
    """
    Convierte nombres generados por ColumnTransformer
    nuevamente a las features originales de PULSO.
    """

    for feature in FEATURES:
        if transformed_name == feature:
            return feature

        if transformed_name.endswith(
            f"__{feature}"
        ):
            return feature

        if transformed_name.startswith(
            f"categorical__{feature}_"
        ):
            return feature

        if transformed_name.startswith(
            f"{feature}_"
        ):
            return feature

    return transformed_name


def explain(
    request: PredictionRequest,
    top_n: int = 3,
) -> ExplanationResponse:
    """
    Genera la explicación SHAP individual para
    una predicción de PULSO.
    """

    pipeline = load_model()

    input_data = pd.DataFrame(
        [
            {
                feature: getattr(
                    request,
                    feature,
                )
                for feature in FEATURES
            }
        ],
        columns=list(FEATURES),
    )

    preprocessor = pipeline.named_steps[
        "preprocessor"
    ]

    transformed = preprocessor.transform(
    input_data[list(FEATURES)]
    )       

    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()

    transformed = np.asarray(transformed)

    feature_names = list(
        preprocessor.get_feature_names_out()
    )

    explainer = get_explainer()

    explanation = explainer(
        transformed
    )

    values = np.asarray(
        explanation.values
    )

    if values.ndim == 3:
        values = values[:, :, 1]

    row_values = values[0]

    # Agrupar contribuciones SHAP por feature original.
    aggregated = {}

    for transformed_name, shap_value in zip(
        feature_names,
        row_values,
    ):
        original_name = (
            _get_original_feature_name(
                transformed_name
            )
        )

        aggregated[original_name] = (
            aggregated.get(
                original_name,
                0.0,
            )
            + float(shap_value)
        )

    sorted_factors = sorted(
        aggregated.items(),
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    top_factors = []

    for feature, shap_value in sorted_factors[
        :top_n
    ]:
        value = getattr(
            request,
            feature,
            None,
        )

        top_factors.append(
            ShapFactor(
                feature=feature,
                value=float(value),
                shap_value=float(
                    shap_value
                ),
                direction=(
                    "increase"
                    if shap_value >= 0
                    else "decrease"
                ),
            )
        )

    return ExplanationResponse(
        top_factors=top_factors
    )