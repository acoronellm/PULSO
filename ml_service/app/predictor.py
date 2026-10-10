import pandas as pd

from .config import FEATURES, MODEL_THRESHOLD, MODEL_VERSION
from .model_loader import load_model
from .schemas import PredictionRequest, PredictionResponse


def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Ejecuta una predicción utilizando PULSO v1.

    El modelo devuelve la probabilidad asociada a cardio=1.
    La clasificación se obtiene aplicando el threshold oficial.
    """

    model = load_model()

    input_data = pd.DataFrame(
        [
            {
                feature: getattr(request, feature)
                for feature in FEATURES
            }
        ],
        columns=FEATURES,
    )

    probabilities = model.predict_proba(input_data)

    probability = float(probabilities[0][1])

    classification = int(
        probability >= MODEL_THRESHOLD
    )

    return PredictionResponse(
        probability=probability,
        classification=classification,
        threshold=MODEL_THRESHOLD,
        model_version=MODEL_VERSION,
    )