import os

import httpx
import pytest


BACKEND_URL = os.getenv(
    "PULSO_BACKEND_URL",
    "http://localhost:8000",
).rstrip("/")

ML_URL = os.getenv(
    "PULSO_ML_URL",
    "http://localhost:8001",
).rstrip("/")


USER_DATA = {
    "gender": 1,
    "height": 172,
    "weight": 72,
    "ap_hi": 120,
    "ap_lo": 80,
    "smoke": 0,
    "alco": 0,
    "active": 1,
    "age_years": 50,
    "bmi": 24.34,
}


@pytest.fixture(scope="session")
def client():
    with httpx.Client(timeout=420.0) as http_client:
        yield http_client


def test_pi01_backend_and_ml_service_are_available(client):
    backend_response = client.get(
        f"{BACKEND_URL}/api/health"
    )

    ml_response = client.get(
        f"{ML_URL}/health"
    )

    assert backend_response.status_code == 200
    assert ml_response.status_code == 200

    backend_body = backend_response.json()
    ml_body = ml_response.json()

    assert backend_body["status"] == "ok"

    assert ml_body["status"] == "ok"
    assert ml_body["model_loaded"] is True
    assert ml_body["model_version"] == "v1"


def test_pi02_complete_analysis_flow(client):
    response = client.post(
        f"{BACKEND_URL}/api/analyze",
        json=USER_DATA,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert "prediction" in body
    assert "shap" in body
    assert "rag" in body

    prediction = body["prediction"]

    assert 0 <= prediction["probability"] <= 1
    assert prediction["classification"] in [0, 1]
    assert prediction["threshold"] == 0.38
    assert prediction["model_version"] == "v1"

    shap = body["shap"]

    assert "top_factors" in shap
    assert isinstance(shap["top_factors"], list)
    assert len(shap["top_factors"]) > 0

    for factor in shap["top_factors"]:
        assert "feature" in factor
        assert "value" in factor
        assert "shap_value" in factor
        assert factor["direction"] in [
            "increase",
            "decrease",
        ]

    rag = body["rag"]

    assert isinstance(rag["summary"], str)
    assert len(rag["summary"]) > 0
    assert isinstance(rag["recommendations"], list)
    assert isinstance(rag["considerations"], str)
    assert isinstance(rag["note"], str)
    assert isinstance(
        rag["insufficient_information"],
        bool,
    )


def test_pi03_complete_simulation_flow(client):
    payload = {
        "original": USER_DATA,
        "changes": {
            "weight": 80,
            "ap_hi": 130,
            "smoke": 0,
            "active": 1,
        },
    }

    response = client.post(
        f"{BACKEND_URL}/api/simulate",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert "original" in body
    assert "simulated" in body
    assert "probability_difference" in body
    assert "applied_changes" in body

    assert 0 <= body["original"]["probability"] <= 1
    assert 0 <= body["simulated"]["probability"] <= 1

    assert body["original"]["classification"] in [0, 1]
    assert body["simulated"]["classification"] in [0, 1]

    assert body["model_version"] == "v1"
    assert body["threshold"] == 0.38

    assert body["applied_changes"]["weight"] == 80
    assert body["applied_changes"]["ap_hi"] == 130


def test_pi04_rag_preserves_source_traceability(client):
    response = client.post(
        f"{BACKEND_URL}/api/analyze",
        json=USER_DATA,
    )

    assert response.status_code == 200, response.text

    rag = response.json()["rag"]

    recommendations = rag["recommendations"]

    assert len(recommendations) > 0

    recommendations_with_sources = 0

    for recommendation in recommendations:
        assert "factor" in recommendation
        assert "recommendation" in recommendation
        assert "source_ids" in recommendation
        assert "sources" in recommendation

        if recommendation["sources"]:
            recommendations_with_sources += 1

            for source in recommendation["sources"]:
                assert "source_id" in source
                assert "source" in source
                assert "score" in source
                assert "lines" in source
                assert "from" in source["lines"]
                assert "to" in source["lines"]

    assert recommendations_with_sources > 0