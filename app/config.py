from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Application
    app_name: str = "AI Time Entry Rewrite"
    app_version: str = "1.0.0"
    debug: bool = False

    # Security
    secret_key: str = "CHANGE-ME-IN-PRODUCTION-USE-LONG-RANDOM-STRING"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS - Comma-separated list of allowed origins
    cors_origins: str = "http://localhost:3000,http://localhost:9001,http://127.0.0.1:9001"

    # Database
    database_url: str = "sqlite:///./time_rewrite.db"

    # LLM Configuration
    ollama_url: str = "http://localhost:11434/api/generate"
    model_name: str = "qwen2.5:7b"
    llm_timeout: int = 90

    # File Upload Limits (in bytes)
    max_upload_size: int = 10 * 1024 * 1024  # 10MB default
    allowed_upload_extensions: List[str] = [".pdf"]

    # Rate Limiting (requests per minute)
    rate_limit_per_minute: int = 60

    # Password Requirements
    min_password_length: int = 8

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
