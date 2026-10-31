from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes.analysis import analysis_cache
from backend.app.schemas.analysis import (
    PredictionData,
    ShapData,
    UserData,
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

PREDICTION = PredictionData(
    probability=0.35,
    threshold=0.38,
    classification=0,
    model_version="v1",
)

SHAP = ShapData(
    top_factors=[
        {
            "feature": "ap_hi",
            "value": 150,
            "shap_value": 0.44,
            "direction": "increase",
        }
    ]
)


def store_valid_analysis():
    return analysis_cache.store(
        UserData.model_validate(VALID_PAYLOAD),
        PREDICTION,
        SHAP,
    )


def rag_payload(analysis_id):
    return {"analysis_id": str(analysis_id)}


def test_rag_route(monkeypatch):
    analysis_id = store_valid_analysis()

    async def fake_generate_recommendations(payload):
        assert payload.prediction == PREDICTION
        assert payload.user_data == UserData.model_validate(VALID_PAYLOAD)
        assert payload.shap == SHAP
        return {
            "summary": "Resumen de prueba.",
            "recommendations": [],
            "considerations": "Consideraciones de prueba.",
            "note": "PULSO ofrece información educativa.",
            "insufficient_information": False,
        }

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/rag",
        json=rag_payload(analysis_id),
    )

    assert response.status_code == 200
    assert response.json()["summary"] == "Resumen de prueba."


def test_rag_route_does_not_call_ml(monkeypatch):
    analysis_id = store_valid_analysis()

    async def fail_if_called(user_data):
        raise AssertionError("RAG no debe volver a ejecutar el ML Service")

    async def fake_generate_recommendations(payload):
        return {
            "summary": "Resumen de prueba.",
            "recommendations": [],
            "considerations": "Consideraciones de prueba.",
            "note": "PULSO ofrece información educativa.",
            "insufficient_information": False,
        }

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.generate_prediction",
        fail_if_called,
    )
    monkeypatch.setattr(
        "backend.app.api.routes.analysis.generate_explanation",
        fail_if_called,
    )
    monkeypatch.setattr(
        "backend.app.api.routes.analysis.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/rag",
        json=rag_payload(analysis_id),
    )

    assert response.status_code == 200


def test_rag_route_returns_404_for_unknown_analysis():
    response = client.post(
        "/api/rag",
        json={"analysis_id": "00000000-0000-4000-8000-000000000000"},
    )

    assert response.status_code == 404


def test_rag_route_returns_502_on_rag_error(monkeypatch):
    analysis_id = store_valid_analysis()
    from backend.app.services.rag_client import RagClientError

    async def fake_generate_recommendations(payload):
        raise RagClientError(
            "No fue posible comunicarse con el servicio RAG."
        )

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/rag",
        json=rag_payload(analysis_id),
    )

    assert response.status_code == 502
    assert (
        response.json()["detail"]
        == "No fue posible comunicarse con el servicio RAG."
    )