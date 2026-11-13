from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.infrastructure.config import Settings
from backend.app.infrastructure.database import Base, get_db_session
from backend.app.infrastructure.jwt_access_tokens import JWTAccessTokens
from backend.app.interfaces.http import dependencies
from backend.app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    settings = Settings(
        _env_file=None,
        database_url="sqlite+pysqlite:///:memory:",
        jwt_secret_key="test-key-that-is-at-least-thirty-two-characters",
    )

    def get_test_db_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db_session] = get_test_db_session
    app.dependency_overrides[dependencies.get_settings] = lambda: settings
    app.dependency_overrides[dependencies.get_access_token_issuer] = lambda: JWTAccessTokens(settings)

    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


def test_register_login_and_current_user(client: TestClient):
    registration = client.post(
        "/api/auth/register",
        json={"email": "User@Example.com", "password": "a-very-long-password"},
    )

    assert registration.status_code == 201
    registered = registration.json()
    assert registered["user"]["email"] == "user@example.com"
    assert registered["token_type"] == "bearer"
    assert registered["expires_in"] == 3600
    assert "password_hash" not in registered["user"]

    current_user = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {registered['access_token']}"},
    )
    assert current_user.status_code == 200
    assert current_user.json() == registered["user"]

    login = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "a-very-long-password"},
    )
    assert login.status_code == 200
    assert login.json()["user"] == registered["user"]


def test_authentication_rejects_duplicate_account_and_bad_password(client: TestClient):
    payload = {"email": "user@example.com", "password": "a-very-long-password"}
    assert client.post("/api/auth/register", json=payload).status_code == 201

    duplicate = client.post("/api/auth/register", json=payload)
    assert duplicate.status_code == 409

    invalid_password = client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": "not-the-password"},
    )
    assert invalid_password.status_code == 401
    assert invalid_password.json()["detail"] == "Correo o contraseña incorrectos."


def test_register_validates_password_length_and_email(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "short"},
    )

    assert response.status_code == 422
