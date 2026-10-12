import os

import httpx
from fastapi import FastAPI, HTTPException

from backend.app.schemas.analysis import (
    AnalysisResponse,
    PredictionData,
    RagRequest,
    ShapData,
    SimulationRequest,
    SimulationResponse,
    UserData,
)
from backend.app.services.rag_client import (
    RagClientError,
    generate_recommendations,
)


app = FastAPI(
    title="PULSO Microservices Gateway",
    version="0.1.0",
)


PREDICTION_SERVICE_URL = os.getenv(
    "PREDICTION_SERVICE_URL",
    "http://prediction-service:8001",
)

SHAP_SERVICE_URL = os.getenv(
    "SHAP_SERVICE_URL",
    "http://shap-service:8002",
)

SIMULATION_SERVICE_URL = os.getenv(
    "SIMULATION_SERVICE_URL",
    "http://simulation-service:8003",
)

SERVICE_TIMEOUT = float(
    os.getenv("SERVICE_TIMEOUT_SECONDS", "30")
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "architecture": "microservices",
    }


@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
)
async def analyze(user_data: UserData):
    payload = user_data.model_dump()

    try:
        async with httpx.AsyncClient(
            timeout=SERVICE_TIMEOUT
        ) as client:

            prediction_response = await client.post(
                f"{PREDICTION_SERVICE_URL}/predict",
                json=payload,
            )

            prediction_response.raise_for_status()

            shap_response = await client.post(
                f"{SHAP_SERVICE_URL}/explain",
                json=payload,
            )

            shap_response.raise_for_status()

        prediction = PredictionData.model_validate(
            prediction_response.json()
        )

        shap = ShapData.model_validate(
            shap_response.json()
        )

        rag_request = RagRequest(
            prediction=prediction,
            user_data=user_data,
            shap=shap,
        )

        rag = await generate_recommendations(
            rag_request
        )

        return AnalysisResponse(
            prediction=prediction,
            shap=shap,
            rag=rag,
        )

    except RagClientError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error comunicándose con microservicio: {exc}",
        ) from exc


@app.post(
    "/api/simulate",
    response_model=SimulationResponse,
)
async def simulate_endpoint(
    payload: SimulationRequest,
):
    try:
        async with httpx.AsyncClient(
            timeout=SERVICE_TIMEOUT
        ) as client:

            response = await client.post(
                f"{SIMULATION_SERVICE_URL}/simulate",
                json=payload.model_dump(),
            )

            response.raise_for_status()

        return SimulationResponse.model_validate(
            response.json()
        )

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error comunicándose con simulation service: {exc}",
        ) from exc