from fastapi import FastAPI

from ml_service.app.explainer import explain
from ml_service.app.schemas import PredictionRequest


app = FastAPI(
    title="PULSO SHAP Service",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "shap"}


@app.post("/explain")
def explain_endpoint(payload: PredictionRequest):
    return explain(payload)