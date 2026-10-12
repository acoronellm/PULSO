from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ML Service
    ml_service_url: str = "http://127.0.0.1:8001"
    ml_timeout_seconds: float = 30.0

    # RAG
    rag_service_url: str = ""
    rag_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()