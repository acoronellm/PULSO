"""Pruebas de la API HTTP con los puertos reemplazados por dobles (ver conftest.client)."""

from backend.app.domain.errors import (
    InvalidScenarioError,
    ModelServiceError,
    RecommendationServiceError,
)
from backend.app.domain.entities import (
    DocumentSource,
    FactorExplanation,
    RecommendationReport,
)
from conftest import PROFILE_PAYLOAD

SIMULATION_PAYLOAD = {"original": PROFILE_PAYLOAD, "changes": {"weight": 80}}


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


def test_analyze_returns_422_for_inconsistent_profile(client):
    response = client.post(
        "/api/analyze", json={**PROFILE_PAYLOAD, "ap_hi": 80, "ap_lo": 90})

    assert response.status_code == 422
    assert "ap_hi debe ser mayor que ap_lo" in response.text


def test_analyze_returns_502_on_model_error(client, model):
    model.error = ModelServiceError("ML Service no disponible.")

    response = client.post("/api/analyze", json=PROFILE_PAYLOAD)

    assert response.status_code == 502
    assert response.json()["detail"] == "ML Service no disponible."


def test_rag_uses_stored_analysis_without_running_the_model(client, model, recommendations):
    analysis_id = client.post(
        "/api/analyze", json=PROFILE_PAYLOAD).json()["analysis_id"]
    model.calls.clear()

    response = client.post("/api/rag", json={"analysis_id": analysis_id})

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "Resumen de prueba."
    assert body["recommendations"][0]["sources"][0]["lines"] == {
        "from": 20, "to": 26}
    assert recommendations.received.profile.ap_hi == 150
    assert model.calls == []

def test_rag_exposes_factor_explanations_and_public_sources(client, recommendations):
    source = DocumentSource(
        source_id="SOURCE_3",
        source="Documento sobre presión arterial",
        author="American Heart Association",
        publication_year=2025,
        source_url="https://example.org/documento",
        pdf_url=None,
        score=None,
        lines=None,
    )

    recommendations.report = RecommendationReport(
        summary="Resumen de prueba.",
        considerations="Una medición aislada no confirma un diagnóstico.",
        note="PULSO ofrece información educativa y preventiva.",
        insufficient_information=False,
        recommendations=(),
        factor_explanations=(
            FactorExplanation(
                query_group="blood_pressure",
                factor="presión arterial",
                features=("ap_hi", "ap_lo"),
                explanation="La presión arterial está relacionada con la salud cardiovascular.",
                source_ids=("SOURCE_3",),
                sources=(source,),
            ),
        ),
    )

    analysis_id = client.post(
        "/api/analyze",
        json=PROFILE_PAYLOAD,
    ).json()["analysis_id"]

    response = client.post(
        "/api/rag",
        json={"analysis_id": analysis_id},
    )

    assert response.status_code == 200

    body = response.json()

    assert set(body) == {
        "summary",
        "recommendations",
        "factor_explanations",
        "considerations",
        "note",
        "insufficient_information",
    }

    assert body["recommendations"] == []
    assert body["insufficient_information"] is False

    assert len(body["factor_explanations"]) == 1

    explanation = body["factor_explanations"][0]

    assert explanation["query_group"] == "blood_pressure"
    assert explanation["factor"] == "presión arterial"
    assert explanation["features"] == ["ap_hi", "ap_lo"]
    assert explanation["source_ids"] == ["SOURCE_3"]
    assert explanation["explanation"] == (
        "La presión arterial está relacionada con la salud cardiovascular."
    )

    assert explanation["sources"] == [
        {
            "source_id": "SOURCE_3",
            "source": "Documento sobre presión arterial",
            "author": "American Heart Association",
            "publication_year": 2025,
            "source_url": "https://example.org/documento",
            "pdf_url": None,
            "score": None,
            "lines": None,
        }
    ]

    assert body["considerations"] == (
        "Una medición aislada no confirma un diagnóstico."
    )

    assert "retrieval_evaluation" not in body
    assert "validation_audit" not in body

def test_rag_returns_404_for_unknown_analysis(client):
    response = client.post(
        "/api/rag",
        json={"analysis_id": "00000000-0000-4000-8000-000000000000"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El análisis no existe o ya expiró."


def test_rag_returns_502_on_rag_error(client, recommendations):
    analysis_id = client.post(
        "/api/analyze", json=PROFILE_PAYLOAD).json()["analysis_id"]
    recommendations.error = RecommendationServiceError(
        "No fue posible comunicarse con el servicio RAG."
    )

    response = client.post("/api/rag", json={"analysis_id": analysis_id})

    assert response.status_code == 502
    assert response.json()[
        "detail"] == "No fue posible comunicarse con el servicio RAG."


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
        json={"original": {**PROFILE_PAYLOAD, "ap_hi": 80,
                           "ap_lo": 90}, "changes": {"weight": 80}},
    )

    assert response.status_code == 422


def test_simulate_returns_422_on_invalid_scenario(client, model):
    model.error = InvalidScenarioError(
        "El escenario de simulación no es válido.")

    response = client.post("/api/simulate", json=SIMULATION_PAYLOAD)

    assert response.status_code == 422
    assert response.json()[
        "detail"] == "El escenario de simulación no es válido."


def test_simulate_returns_502_on_model_error(client, model):
    model.error = ModelServiceError("ML Service no disponible.")

    response = client.post("/api/simulate", json=SIMULATION_PAYLOAD)

    assert response.status_code == 502
