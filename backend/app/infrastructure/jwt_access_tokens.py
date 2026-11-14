from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from .config import Settings


class JWTAccessTokens:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret_key
        self._expires_minutes = settings.access_token_expire_minutes

    def issue(self, user_id: UUID) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self._expires_minutes)
        return jwt.encode(
            {"sub": str(user_id), "exp": expires_at},
            self._secret,
            algorithm="HS256",
        )

    def subject(self, token: str) -> UUID:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                options={"require": ["exp", "sub"]},
            )
            return UUID(claims["sub"])
        except (jwt.InvalidTokenError, ValueError, KeyError, TypeError) as error:
            raise ValueError("Invalid access token.") from error
