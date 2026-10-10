from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_simulation_route(monkeypatch):
    async def fake_simulate_scenario(payload):
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

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.simulate_scenario",
        fake_simulate_scenario,
    )

    payload = {
        "original": {
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
        "changes": {
            "weight": 80,
        },
    }

    response = client.post(
        "/api/simulate",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["original"]["probability"] == 0.80
    assert body["simulated"]["probability"] == 0.50
    assert body["probability_difference"] == -0.30