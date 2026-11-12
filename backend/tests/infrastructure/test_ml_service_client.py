import json

import httpx
import pytest

from backend.app.domain.entities import ScenarioChanges
from backend.app.domain.errors import InvalidScenarioError, ModelServiceError
from backend.app.infrastructure.ml_service_client import MLServiceClient

from conftest import PROFILE, PROFILE_PAYLOAD

SIMULATION_RESPONSE = {
    "original": {"probability": 0.80, "classification": 1},
    "simulated": {"probability": 0.50, "classification": 1},
    "probability_difference": -0.30,
    "applied_changes": {"weight": 80},
    "model_version": "v1",
    "threshold": 0.38,
}


def client_returning(status_code: int, body, requests: list | None = None) -> MLServiceClient:
    def handler(request: httpx.Request) -> httpx.Response:
        if requests is not None:
            requests.append(request)
        return httpx.Response(status_code, json=body)

    return MLServiceClient(
        base_url="http://ml-service:8001/",
        timeout_seconds=5,
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
async def test_predict_sends_profile_and_returns_prediction():
    requests = []
    client = client_returning(
        200,
        {"probability": 0.35, "classification": 0, "threshold": 0.38, "model_version": "v1"},
        requests,
    )

    prediction = await client.predict(PROFILE)

    assert prediction.probability == 0.35
    assert prediction.threshold == 0.38
    assert str(requests[0].url) == "http://ml-service:8001/predict"
    assert json.loads(requests[0].content) == PROFILE_PAYLOAD


@pytest.mark.asyncio
async def test_explain_returns_shap_factors():
    client = client_returning(
        200,
        {"top_factors": [{"feature": "ap_hi", "value": 150, "shap_value": 0.44, "direction": "increase"}]},
    )

    explanation = await client.explain(PROFILE)

    assert explanation.top_factors[0].feature == "ap_hi"
    assert explanation.top_factors[0].direction == "increase"


@pytest.mark.asyncio
async def test_simulate_returns_valid_outcome():
    requests = []
    client = client_returning(200, SIMULATION_RESPONSE, requests)

    outcome = await client.simulate(PROFILE, ScenarioChanges(weight=80))

    assert outcome.original.probability == 0.80
    assert outcome.simulated.probability == 0.50
    assert outcome.threshold == 0.38
    assert outcome.model_version == "v1"
    body = json.loads(requests[0].content)
    assert body["original"] == PROFILE_PAYLOAD
    assert body["changes"]["weight"] == 80


@pytest.mark.asyncio
async def test_simulate_rejects_invalid_response():
    client = client_returning(200, {"invalid": "response"})

    with pytest.raises(ModelServiceError, match="simulación no cumple el contrato"):
        await client.simulate(PROFILE, ScenarioChanges(weight=80))


@pytest.mark.asyncio
async def test_simulate_maps_422_to_invalid_scenario():
    client = client_returning(422, {"detail": "invalid"})

    with pytest.raises(InvalidScenarioError, match="El escenario de simulación no es válido."):
        await client.simulate(PROFILE, ScenarioChanges(ap_hi=130))


@pytest.mark.asyncio
async def test_http_errors_raise_model_service_error():
    client = client_returning(500, {})

    with pytest.raises(ModelServiceError, match="HTTP 500 al generar SHAP"):
        await client.explain(PROFILE)


@pytest.mark.asyncio
async def test_connection_errors_raise_model_service_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin conexión", request=request)

    client = MLServiceClient("http://ml-service:8001", 5, transport=httpx.MockTransport(handler))

    with pytest.raises(ModelServiceError, match="No fue posible comunicarse con el ML Service."):
        await client.predict(PROFILE)
