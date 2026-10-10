from fastapi import FastAPI, HTTPException
from .explainer import explain
from .config import MODEL_VERSION
from .model_loader import load_model
from .predictor import predict
from .schemas import (PredictionRequest, PredictionResponse, ExplanationResponse, SimulationRequest, SimulationResponse,
SimulationResponse)
from .simulator import simulate


app = FastAPI(
    title="PULSO ML Service",
    version="0.1.0",
)


@app.get("/health")
def health():
    try:
        load_model()

        return {
            "status": "ok",
            "service": "ml-service",
            "model_loaded": True,
            "model_version": MODEL_VERSION,
        }

    except Exception:
        return {
            "status": "error",
            "service": "ml-service",
            "model_loaded": False,
            "model_version": MODEL_VERSION,
        }


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict_endpoint(
    request: PredictionRequest,
):
    return predict(request)

@app.post(
    "/explain",
    response_model=ExplanationResponse,
)
def explain_endpoint(
    request: PredictionRequest,
):
    try:
        return explain(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="No fue posible generar la explicación SHAP.",
        ) from exc
@app.post(
    "/simulate",
    response_model=SimulationResponse,
)
def simulate_endpoint(
    request: SimulationRequest,
):
    try:
        return simulate(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "No fue posible ejecutar "
                "la simulación."
            ),
        ) from exc