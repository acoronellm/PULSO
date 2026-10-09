from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración general del backend de PULSO.

    Los valores pueden cargarse desde variables de entorno
    o desde un archivo .env durante desarrollo local.
    """

    rag_service_url: str = ""
    rag_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()