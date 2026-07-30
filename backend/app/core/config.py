from functools import lru_cache
import json
from typing import Any, List, Union
from pydantic import Field, field_validator
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
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "https://*.vercel.app"],
        description="Allowed CORS origin URLs"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """
        Parses JSON array strings or comma-separated strings into a valid list of origin strings.
        """
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return ["http://localhost:5173", "http://localhost:3000", "https://*.vercel.app"]
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed]
                except Exception:
                    pass
            return [i.strip() for i in v_str.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(item) for item in v]
        return ["http://localhost:5173", "http://localhost:3000", "https://*.vercel.app"]

    # Supabase & Database Configuration (Defaults to active Supabase Cloud PostgreSQL database)
    DATABASE_URL: str = Field(
        default="postgresql://postgres.oehendzrfyjyklppwkfv:Route_AI_Opti@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?pgbouncer=true",
        description="Database connection string with async driver specification"
    )
    SUPABASE_URL: str = Field(
        default="https://oehendzrfyjyklppwkfv.supabase.co",
        description="Supabase Project API Endpoint URL"
    )
    SUPABASE_ANON_KEY: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9laGVuZHpyZnlqeWtscHB3a2Z2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUzMTA1NjIsImV4cCI6MjEwMDg4NjU2Mn0.3qsfsqB2L6zCWpl6qE4B1I44vz7XcOoZYilesp-Tv8Q",
        description="Supabase Anonymous API Key"
    )
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9laGVuZHpyZnlqeWtscHB3a2Z2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTMxMDU2MiwiZXhwIjoyMTAwODg2NTYyfQ.bYRfQNrJOVwLST7NjD7L24eAJ8XWNmigT2yDzHGtjCc",
        description="Supabase Service Role Key"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        """
        Ensures the database connection URL uses the asyncpg driver for PostgreSQL or aiosqlite for SQLite.
        Converts 'postgres://' or 'postgresql://' prefixes to 'postgresql+asyncpg://'.
        Strips invalid query parameters like '?pgbouncer=true' that asyncpg does not accept.
        """
        if isinstance(v, str):
            v_clean = v.strip()
            if "?" in v_clean:
                v_clean = v_clean.split("?", 1)[0]
            if v_clean.startswith("postgres://"):
                return v_clean.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v_clean.startswith("postgresql://") and not v_clean.startswith("postgresql+asyncpg://"):
                return v_clean.replace("postgresql://", "postgresql+asyncpg://", 1)
            return v_clean
        return v

    DB_POOL_SIZE: int = Field(default=10, description="SQLAlchemy engine pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="SQLAlchemy engine max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="SQLAlchemy engine pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=1800, description="SQLAlchemy connection recycle time in seconds")
    DB_ECHO: bool = Field(default=False, description="Enable SQLAlchemy SQL query log output")

    # Security & JWT Configuration
    JWT_SECRET_KEY: str = Field(
        default="+w8zlOq7zv3DSy2kwVmjCPC1HQ6f7A52w/xIRffEZt3yVUK6kPJwlrBmxjUJLe/znRKK1NNOFE1yrw6gLxZkNA==",
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


settings = get_settings()
