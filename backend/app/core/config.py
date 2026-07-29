from functools import lru_cache
from typing import Any, List, Union
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Enterprise Settings Management using Pydantic v2 BaseSettings.
    Automatically loads and validates environment variables from `.env` files.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # General App Environment
    ENVIRONMENT: str = Field(default="development", description="Execution environment: development, staging, production")
    PROJECT_NAME: str = Field(default="RouteAI Enterprise Logistics Platform", description="Application Title")
    API_V1_STR: str = Field(default="/api/v1", description="API Version 1 Prefix")
    DEBUG: bool = Field(default=True, description="Enable debug mode")

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Bind host address")
    PORT: int = Field(default=8000, description="Bind port number")

    # CORS Settings
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origin URLs"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Union[List[str], str]:
        """
        Parses comma-separated string origins or lists into a valid list of strings.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"Invalid CORS origins value: {v}")

    # Database Configuration (Supabase PostgreSQL / Async Driver)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/routeai_db",
        description="Database connection string with async driver specification"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        """
        Ensures the database connection URL uses the asyncpg driver for SQLAlchemy 2.0.
        Converts 'postgres://' or 'postgresql://' prefixes to 'postgresql+asyncpg://'.
        """
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    DB_POOL_SIZE: int = Field(default=10, description="SQLAlchemy engine pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="SQLAlchemy engine max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="SQLAlchemy engine pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=1800, description="SQLAlchemy connection recycle time in seconds")
    DB_ECHO: bool = Field(default=False, description="Enable SQLAlchemy SQL query log output")

    # Security & JWT Configuration
    JWT_SECRET_KEY: str = Field(
        default="dev-jwt-secret-key-change-this-in-production-1234567890",
        description="Secret key for signing JWT tokens"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="Cryptographic algorithm for JWT signature")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Access token expiration window in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration window in days")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging verbosity level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or console")


@lru_cache()
def get_settings() -> Settings:
    """
    Retrieves a cached instance of the application Settings.
    Utilizes LRU Cache to avoid redundant file I/O and environment parsing.
    """
    return Settings()


# Export default global settings instance for immediate module imports
settings = get_settings()
