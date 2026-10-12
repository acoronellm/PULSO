from fastapi.testclient import TestClient

from ml_service.app.main import app


client = TestClient(app)


def test_ml_service_health(monkeypatch):
    monkeypatch.setattr(
        "ml_service.app.main.load_model",
        lambda: object(),
    )

    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["service"] == "ml-service"
    assert body["model_loaded"] is True
    assert body["model_version"] == "v1"