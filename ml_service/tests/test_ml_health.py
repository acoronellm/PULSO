from fastapi.testclient import TestClient

from ml_service.app.main import app


client = TestClient(app)


def test_ml_service_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ml-service",
        "model_loaded": False,
    }