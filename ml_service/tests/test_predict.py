from fastapi.testclient import TestClient

from ml_service.app.main import app


client = TestClient(app)


VALID_PAYLOAD = {
    "gender": 1,
    "height": 170,
    "weight": 80,
    "ap_hi": 150,
    "ap_lo": 90,
    "smoke": 0,
    "alco": 0,
    "active": 1,
    "age_years": 55,
    "bmi": 27.68,
}


def test_predict_returns_expected_structure():
    response = client.post(
        "/predict",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    body = response.json()

    assert set(body.keys()) == {
        "probability",
        "classification",
        "threshold",
        "model_version",
    }

    assert 0 <= body["probability"] <= 1
    assert body["classification"] in [0, 1]
    assert body["threshold"] == 0.38
    assert body["model_version"] == "v1"


def test_predict_classification_matches_threshold():
    response = client.post(
        "/predict",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    body = response.json()

    expected_classification = int(
        body["probability"] >= body["threshold"]
    )

    assert body["classification"] == expected_classification


def test_predict_rejects_invalid_blood_pressure():
    invalid_payload = {
        **VALID_PAYLOAD,
        "ap_hi": 80,
        "ap_lo": 90,
    }

    response = client.post(
        "/predict",
        json=invalid_payload,
    )

    assert response.status_code == 422


def test_predict_rejects_invalid_binary_feature():
    invalid_payload = {
        **VALID_PAYLOAD,
        "smoke": 2,
    }

    response = client.post(
        "/predict",
        json=invalid_payload,
    )

    assert response.status_code == 422