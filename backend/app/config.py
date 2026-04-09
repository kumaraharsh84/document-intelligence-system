from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 1440
    database_url: str = "sqlite+aiosqlite:///./app.db"
    storage_backend: str = "local"
    local_upload_dir: str = "./uploads"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "us-east-1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    google_api_key: str = ""
    ocr_engine: str = "tesseract"
    ai_provider: str = "openai"
    max_file_size_mb: int = 10
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        """Split the configured CORS origins into a normalized list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Return whether the app is running in a production-like environment."""
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cache settings so repeated imports reuse the same configuration object."""
    return Settings()


settings = get_settings()
