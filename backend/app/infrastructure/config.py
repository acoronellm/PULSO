from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Authentication and PostgreSQL
    database_url: str = "postgresql+psycopg://pulso:pulso@localhost:5432/pulso"
    jwt_secret_key: str
    access_token_expire_minutes: int = Field(default=60, gt=0, le=1440)

    # ML Service
    ml_service_url: str = "http://127.0.0.1:8001"
    ml_timeout_seconds: float = 30.0

    # RAG
    rag_service_url: str = ""
    rag_timeout_seconds: float = 30.0

    # In-memory analysis context cache
    analysis_cache_ttl_seconds: float = 900.0
    analysis_cache_max_entries: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        if len(value) < 32 or value.startswith("replace_with_"):
            raise ValueError("JWT_SECRET_KEY must be a private random value of at least 32 characters.")
        return value
