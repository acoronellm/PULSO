from fastapi import FastAPI

from ml_service.app.predictor import predict
from ml_service.app.schemas import PredictionRequest


app = FastAPI(
    title="PULSO Prediction Service",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "prediction"}


@app.post("/predict")
def predict_endpoint(payload: PredictionRequest):
    return predict(payload)