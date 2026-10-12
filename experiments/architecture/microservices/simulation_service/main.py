from fastapi import FastAPI

from ml_service.app.schemas import SimulationRequest
from ml_service.app.simulator import simulate


app = FastAPI(
    title="PULSO Simulation Service",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "simulation"}


@app.post("/simulate")
def simulate_endpoint(payload: SimulationRequest):
    return simulate(payload)