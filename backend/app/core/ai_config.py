import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """
    Configuration settings for Google Gemini API, RAG Architecture, and Multi-Agent Engine.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    GEMINI_API_KEY: str = Field(
        default=os.getenv("GEMINI_API_KEY", ""),
        description="Google Gemini API key for generative LLM calls"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Google Gemini LLM model identifier"
    )
    EMBEDDING_DIMENSION: int = Field(
        default=384,
        description="Vector embedding dimension size for semantic search"
    )
    RAG_CHUNK_SIZE: int = Field(
        default=300,
        description="Word count per document chunk for RAG indexing"
    )
    RAG_CHUNK_OVERLAP: int = Field(
        default=50,
        description="Overlapping word count between consecutive RAG chunks"
    )


ai_settings = AISettings()
