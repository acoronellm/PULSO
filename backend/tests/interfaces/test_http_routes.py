"""Pruebas de la API HTTP con los puertos reemplazados por dobles (ver conftest.client)."""

from uuid import uuid4

from backend.app.domain.errors import (
    InvalidScenarioError,
    ModelServiceError,
    RecommendationServiceError,
)
from backend.app.domain.entities import AuthUser
from backend.app.main import create_app
from backend.app.interfaces.http import dependencies
from fastapi.testclient import TestClient

from conftest import PROFILE_PAYLOAD

SIMULATION_PAYLOAD = {"original": PROFILE_PAYLOAD, "changes": {"weight": 80}}


def test_analysis_requires_authentication():
    app = create_app()
    app.dependency_overrides[dependencies.get_user_repository] = lambda: None
    app.dependency_overrides[dependencies.get_access_token_issuer] = lambda: None
    app.dependency_overrides[dependencies.get_analyze_profile] = lambda: None
    response = TestClient(app).post("/api/analyze", json=PROFILE_PAYLOAD)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "backend"}


def test_analyze_returns_prediction_and_shap_without_rag(client):
    response = client.post("/api/analyze", json=PROFILE_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["analysis_id"]
    assert body["prediction"]["probability"] == 0.35
    assert body["prediction"]["threshold"] == 0.38
    assert body["shap"]["top_factors"][0]["feature"] == "ap_hi"
    assert "rag" not in body


def test_analysis_history_returns_only_the_authenticated_users_results(client):
    owner_id = client.app.dependency_overrides[dependencies.get_current_user]().id
    response = client.post("/api/analyze", json=PROFILE_PAYLOAD)
    analysis_id = response.json()["analysis_id"]

    first_page = client.get("/api/analyses?limit=1&offset=0")

    assert first_page.status_code == 200
    body = first_page.json()
    assert body["has_more"] is False
    assert len(body["items"]) == 1
    assert body["items"][0]["analysis_id"] == analysis_id
    assert body["items"][0]["prediction"]["probability"] == 0.35
    assert "profile" not in body["items"][0]

    client.app.dependency_overrides[dependencies.get_current_user] = lambda: AuthUser(
        id=uuid4(),
        email="other@example.com",
        password_hash="",
    )
    other_user_history = client.get("/api/analyses")

    assert other_user_history.status_code == 200
    assert other_user_history.json()["items"] == []


def test_analysis_history_is_paginated(client):
    for _ in range(3):
        response = client.post("/api/analyze", json=PROFILE_PAYLOAD)
        assert response.status_code == 200

    first_page = client.get("/api/analyses?limit=2&offset=0").json()
    second_page = client.get("/api/analyses?limit=2&offset=2").json()

    assert len(first_page["items"]) == 2
    assert first_page["has_more"] is True
    assert len(second_page["items"]) == 1
    assert second_page["has_more"] is False


def test_analyze_returns_422_for_inconsistent_profile(client):
    response = client.post("/api/analyze", json={**PROFILE_PAYLOAD, "ap_hi": 80, "ap_lo": 90})

    assert response.status_code == 422
    assert "ap_hi debe ser mayor que ap_lo" in response.text


def test_analyze_returns_502_on_model_error(client, model):
    model.error = ModelServiceError("ML Service no disponible.")

    response = client.post("/api/analyze", json=PROFILE_PAYLOAD)

    assert response.status_code == 502
    assert response.json()["detail"] == "ML Service no disponible."


def test_rag_uses_stored_analysis_without_running_the_model(client, model, recommendations):
    analysis_id = client.post("/api/analyze", json=PROFILE_PAYLOAD).json()["analysis_id"]
    model.calls.clear()

    response = client.post("/api/rag", json={"analysis_id": analysis_id})

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "Resumen de prueba."
    assert body["recommendations"][0]["sources"][0]["lines"] == {"from": 20, "to": 26}
    assert recommendations.received.profile.ap_hi == 150
    assert model.calls == []


def test_rag_analysis_is_scoped_to_the_authenticated_user(client):
    analysis_id = client.post("/api/analyze", json=PROFILE_PAYLOAD).json()["analysis_id"]
    client.app.dependency_overrides[dependencies.get_current_user] = lambda: AuthUser(
        id=uuid4(),
        email="other@example.com",
        password_hash="",
    )

    response = client.post("/api/rag", json={"analysis_id": analysis_id})

    assert response.status_code == 404


def test_rag_returns_404_for_unknown_analysis(client):
    response = client.post(
        "/api/rag",
        json={"analysis_id": "00000000-0000-4000-8000-000000000000"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El análisis no existe o ya expiró."


def test_rag_returns_502_on_rag_error(client, recommendations):
    analysis_id = client.post("/api/analyze", json=PROFILE_PAYLOAD).json()["analysis_id"]
    recommendations.error = RecommendationServiceError(
        "No fue posible comunicarse con el servicio RAG."
    )

    response = client.post("/api/rag", json={"analysis_id": analysis_id})

    assert response.status_code == 502
    assert response.json()["detail"] == "No fue posible comunicarse con el servicio RAG."


def test_simulate_returns_model_outcome(client, model):
    response = client.post("/api/simulate", json=SIMULATION_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["original"]["probability"] == 0.80
    assert body["simulated"]["probability"] == 0.50
    assert body["probability_difference"] == -0.30
    profile, changes = model.simulated_with
    assert profile.weight == 88
    assert changes.as_dict() == {"weight": 80}


def test_simulate_rejects_invalid_payload(client):
    response = client.post(
        "/api/simulate",
        json={"original": {**PROFILE_PAYLOAD, "ap_hi": 80, "ap_lo": 90}, "changes": {"weight": 80}},
    )

    assert response.status_code == 422


def test_simulate_returns_422_on_invalid_scenario(client, model):
    model.error = InvalidScenarioError("El escenario de simulación no es válido.")

    response = client.post("/api/simulate", json=SIMULATION_PAYLOAD)

    assert response.status_code == 422
    assert response.json()["detail"] == "El escenario de simulación no es válido."


def test_simulate_returns_502_on_model_error(client, model):
    model.error = ModelServiceError("ML Service no disponible.")

    response = client.post("/api/simulate", json=SIMULATION_PAYLOAD)

    assert response.status_code == 502
