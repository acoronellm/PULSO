import httpx
import pytest

from backend.app.core.config import settings
from backend.app.schemas.analysis import (
    SimulationRequest,
)
from backend.app.services.ml_client import (
    MLClientError,
    simulate_scenario,
)


@pytest.mark.asyncio
async def test_simulate_scenario_returns_valid_response(
    monkeypatch,
):
    payload = SimulationRequest(
        original={
            "gender": 1,
            "height": 172,
            "weight": 88,
            "ap_hi": 150,
            "ap_lo": 92,
            "smoke": 1,
            "alco": 0,
            "active": 0,
            "age_years": 61,
            "bmi": 29.75,
        },
        changes={
            "weight": 80,
        },
    )

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "original": {
                    "probability": 0.80,
                    "classification": 1,
                },
                "simulated": {
                    "probability": 0.50,
                    "classification": 1,
                },
                "probability_difference": -0.30,
                "applied_changes": {
                    "weight": 80,
                },
                "model_version": "v1",
                "threshold": 0.38,
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            pass

        async def post(
            self,
            url,
            json,
        ):
            return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    monkeypatch.setattr(
        settings,
        "ml_service_url",
        "http://ml-service:8001",
    )

    result = await simulate_scenario(
        payload
    )

    assert result.original.probability == 0.80
    assert result.simulated.probability == 0.50
    assert result.threshold == 0.38
    assert result.model_version == "v1"

@pytest.mark.asyncio
async def test_simulate_scenario_rejects_invalid_response(
    monkeypatch,
):
    payload = SimulationRequest(
        original={
            "gender": 1,
            "height": 172,
            "weight": 88,
            "ap_hi": 150,
            "ap_lo": 92,
            "smoke": 1,
            "alco": 0,
            "active": 0,
            "age_years": 61,
            "bmi": 29.75,
        },
        changes={
            "weight": 80,
        },
    )

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "invalid": "response"
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            pass

        async def post(
            self,
            url,
            json,
        ):
            return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    with pytest.raises(
        MLClientError,
    ):
        await simulate_scenario(
            payload
        )