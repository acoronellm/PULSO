from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.analysis import (
    PredictionData,
    ShapData,
)
from backend.app.services.ml_client import (
    MLClientError,
)


client = TestClient(app)


VALID_PAYLOAD = {
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
}


def test_analyze_returns_prediction_and_shap_without_rag(
    monkeypatch,
):
    async def fake_generate_prediction(
        user_data,
    ):
        return PredictionData(
            probability=0.35,
            classification=0,
            threshold=0.38,
            model_version="v1",
        )

    async def fake_generate_explanation(
        user_data,
    ):
        return ShapData(
            top_factors=[
                {
                    "feature": "ap_hi",
                    "value": 150,
                    "shap_value": 0.44,
                    "direction": "increase",
                }
            ]
        )

    monkeypatch.setattr(
        "backend.app.api.routes.analysis."
        "generate_prediction",
        fake_generate_prediction,
    )

    monkeypatch.setattr(
        "backend.app.api.routes.analysis."
        "generate_explanation",
        fake_generate_explanation,
    )

    response = client.post(
        "/api/analyze",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["analysis_id"]
    assert body["prediction"]["probability"] == 0.35
    assert body["prediction"]["threshold"] == 0.38

    assert (
        body["shap"]["top_factors"][0]["feature"]
        == "ap_hi"
    )
    assert "rag" not in body


def test_analyze_returns_502_on_ml_error(
    monkeypatch,
):
    async def fake_generate_prediction(
        user_data,
    ):
        raise MLClientError(
            "ML Service no disponible."
        )

    monkeypatch.setattr(
        "backend.app.api.routes.analysis."
        "generate_prediction",
        fake_generate_prediction,
    )

    response = client.post(
        "/api/analyze",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 502
