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
