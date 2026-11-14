from uuid import uuid4

import pytest

from backend.app.infrastructure.config import Settings
from backend.app.infrastructure.jwt_access_tokens import JWTAccessTokens


def test_access_token_round_trips_user_subject():
    tokens = JWTAccessTokens(
        Settings(
            _env_file=None,
            jwt_secret_key="a-test-secret-key-that-is-at-least-thirty-two-characters",
        )
    )
    user_id = uuid4()

    assert tokens.subject(tokens.issue(user_id)) == user_id


def test_access_token_rejects_a_tampered_token():
    tokens = JWTAccessTokens(
        Settings(
            _env_file=None,
            jwt_secret_key="a-test-secret-key-that-is-at-least-thirty-two-characters",
        )
    )

    with pytest.raises(ValueError, match="Invalid access token"):
        tokens.subject("not.a.valid-token")
