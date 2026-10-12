from .config import (
    MODEL_THRESHOLD,
    MODEL_VERSION,
)
from .predictor import predict
from .schemas import (
    PredictionRequest,
    SimulationRequest,
    SimulationResponse,
    SimulationResult,
)


def simulate(
    request: SimulationRequest,
) -> SimulationResponse:

    # Predicción original
    original_prediction = predict(
        request.original
    )

    # Copia de los datos originales
    simulated_data = (
        request.original.model_dump()
    )

    # Aplicar únicamente los cambios enviados
    changes = request.changes.model_dump(
        exclude_none=True
    )

    simulated_data.update(changes)

    # Si cambia el peso, recalcular BMI
    if "weight" in changes:
        height_m = (
            simulated_data["height"] / 100
        )

        simulated_data["bmi"] = (
            simulated_data["weight"]
            / (height_m ** 2)
        )

    # Validar nuevamente el escenario
    simulated_request = PredictionRequest(
        **simulated_data
    )

    # Predicción simulada
    simulated_prediction = predict(
        simulated_request
    )

    return SimulationResponse(
        original=SimulationResult(
            probability=(
                original_prediction.probability
            ),
            classification=(
                original_prediction.classification
            ),
        ),
        simulated=SimulationResult(
            probability=(
                simulated_prediction.probability
            ),
            classification=(
                simulated_prediction.classification
            ),
        ),
        probability_difference=(
            simulated_prediction.probability
            - original_prediction.probability
        ),
        applied_changes=changes,
        model_version=MODEL_VERSION,
        threshold=MODEL_THRESHOLD,
    )