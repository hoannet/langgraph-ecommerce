"""Core configuration and settings."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Provider Selection
    llm_provider: str = Field(
        default="lm_studio",
        description="LLM provider: 'lm_studio', 'gemini', or 'openai'",
    )

    # LM Studio Configuration
    lm_studio_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="LM Studio API base URL",
    )
    lm_studio_model_name: str = Field(
        default="local-model",
        description="Model name in LM Studio",
    )
    lm_studio_api_key: str = Field(
        default="not-needed",
        description="API key (not required for LM Studio)",
    )

    # Google Gemini Configuration
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key",
    )
    gemini_model_name: str = Field(
        default="gemini-pro",
        description="Gemini model name (gemini-pro, gemini-1.5-pro, etc.)",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key",
    )
    openai_model_name: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model name (gpt-4o, gpt-4o-mini, gpt-3.5-turbo, etc.)",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=True, description="Enable auto-reload")

    # Application Settings
    app_name: str = Field(default="LangGraph Chatbot", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    log_level: str = Field(default="INFO", description="Logging level")

    # Paths
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    checkpoint_dir: Path = Field(
        default=Path("./data/checkpoints"),
        description="Checkpoint directory",
    )
    log_dir: Path = Field(default=Path("./data/logs"), description="Log directory")

    # Memory Settings
    max_conversation_history: int = Field(
        default=20,
        description="Maximum conversation history length",
    )
    conversation_summary_threshold: int = Field(
        default=15,
        description="Threshold for conversation summarization",
    )

    # Payment Settings
    payment_mock_mode: bool = Field(
        default=True,
        description="Use mock payment processing",
    )
    payment_timeout: int = Field(default=30, description="Payment timeout in seconds")

    # MongoDB Settings
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL",
    )
    mongodb_db_name: str = Field(
        default="langgraph_ecommerce",
        description="MongoDB database name",
    )

    # LLM Settings
    llm_temperature: float = Field(default=0.7, description="LLM temperature")
    llm_max_tokens: int = Field(default=2048, description="Maximum tokens")
    llm_request_timeout: int = Field(
        default=60,
        description="LLM request timeout in seconds",
    )

    # TiDB Vector Settings
    tidb_connection_string: str = Field(
        default="",
        description="TiDB connection string for vector database",
    )
    tidb_table_name: str = Field(
        default="documents",
        description="TiDB table name for vector storage",
    )
    tidb_embedding_dimension: int = Field(
        default=768,
        description="Embedding dimension (OpenAI: 1536, Gemini: 768, Gemma-300m: 768)",
    )
    tidb_distance_strategy: str = Field(
        default="cosine",
        description="Distance strategy: cosine, l2, or inner_product",
    )
    tidb_search_top_k: int = Field(
        default=4,
        description="Number of documents to retrieve",
    )
    
    # Embedding Provider Settings
    embedding_provider: str = Field(
        default="lm_studio",
        description="Embedding provider: 'openai', 'gemini', or 'lm_studio'",
    )
    lm_studio_embedding_model: str = Field(
        default="google/embedding-gemma-300m",
        description="LM Studio embedding model name",
    )
    
    # RAG Settings
    rag_similarity_threshold: float = Field(
        default=0.35,  # Lower for LM Studio embeddings
        description="Similarity threshold for document relevance (0.0-1.0)",
    )
    rag_use_llm_grading: bool = Field(
        default=False,
        description="Use LLM for document grading (slower, less reliable)",
    )
    rag_use_llm_rewriting: bool = Field(
        default=True,
        description="Use LLM for question rewriting (disabled for LM Studio)",
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize settings and create directories."""
        super().__init__(**kwargs)
        self._create_directories()

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.data_dir, self.checkpoint_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

    @model_validator(mode='after')
    def log_provider_setup(self) -> 'Settings':
        """Log provider configuration for transparency."""
        if self.llm_provider != self.embedding_provider:
            logger.info(
                f"ℹ️  Mixed provider setup: "
                f"LLM={self.llm_provider}, Embedding={self.embedding_provider}. "
                f"Retrieval top_k={self.tidb_search_top_k}"
            )
        else:
            logger.info(
                f"✅ Unified provider setup: {self.llm_provider}"
            )
        return self
