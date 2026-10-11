import httpx

from backend.app.core.config import settings
from backend.app.schemas.analysis import (
    PredictionData,
    ShapData,
    UserData,
    SimulationRequest,
    SimulationResponse
)


class MLClientError(Exception):
    """Error asociado al ML Service."""


async def generate_prediction(
    user_data: UserData,
) -> PredictionData:

    predict_url = (
        f"{settings.ml_service_url.rstrip('/')}"
        "/predict"
    )

    try:
        async with httpx.AsyncClient(
            timeout=settings.ml_timeout_seconds,
        ) as client:
            response = await client.post(
                predict_url,
                json=user_data.model_dump(),
            )

    except httpx.RequestError as exc:
        raise MLClientError(
            "No fue posible comunicarse con el ML Service."
        ) from exc

    if response.status_code >= 400:
        raise MLClientError(
            f"El ML Service respondió con HTTP "
            f"{response.status_code}."
        )

    try:
        return PredictionData.model_validate(
            response.json()
        )

    except Exception as exc:
        raise MLClientError(
            "La respuesta de predicción "
            "no cumple el contrato esperado."
        ) from exc


async def generate_explanation(
    user_data: UserData,
) -> ShapData:

    explain_url = (
        f"{settings.ml_service_url.rstrip('/')}"
        "/explain"
    )

    try:
        async with httpx.AsyncClient(
            timeout=settings.ml_timeout_seconds,
        ) as client:
            response = await client.post(
                explain_url,
                json=user_data.model_dump(),
            )

    except httpx.RequestError as exc:
        raise MLClientError(
            "No fue posible obtener "
            "la explicación del ML Service."
        ) from exc

    if response.status_code >= 400:
        raise MLClientError(
            f"El ML Service respondió con HTTP "
            f"{response.status_code} al generar SHAP."
        )

    try:
        return ShapData.model_validate(
            response.json()
        )

    except Exception as exc:
        raise MLClientError(
            "La explicación SHAP no cumple "
            "el contrato esperado."
        ) from exc

class MLValidationError(Exception):
    """Entrada inválida enviada al ML Service."""
    
async def simulate_scenario(
    payload: SimulationRequest,
) -> SimulationResponse:

    simulate_url = (
        f"{settings.ml_service_url.rstrip('/')}"
        "/simulate"
    )

    try:
        async with httpx.AsyncClient(
            timeout=settings.ml_timeout_seconds,
        ) as client:
            response = await client.post(
                simulate_url,
                json=payload.model_dump(),
            )

    except httpx.RequestError as exc:
        raise MLClientError(
            "No fue posible ejecutar la simulación "
            "en el ML Service."
        ) from exc

    if response.status_code == 422:
        raise MLValidationError(
            "El escenario de simulación no es válido."
        )

    if response.status_code >= 400:
        raise MLClientError(
            f"El ML Service respondió con HTTP "
            f"{response.status_code} al simular."
        )

    try:
        return SimulationResponse.model_validate(
            response.json()
        )

    except Exception as exc:
        raise MLClientError(
            "La respuesta de simulación no cumple "
            "el contrato esperado."
        ) from exc