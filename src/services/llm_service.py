"""LLM service for LM Studio integration."""

from typing import Optional

from langchain_openai import ChatOpenAI

from src.core.config import get_settings
from src.core.exceptions import LLMError
from src.core.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for managing LLM interactions with LM Studio."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        """
        Initialize LLM service.

        Args:
            base_url: LM Studio base URL
            model_name: Model name
            temperature: Temperature setting
            max_tokens: Maximum tokens
        """
        settings = get_settings()

        self.base_url = base_url or settings.lm_studio_base_url
        self.model_name = model_name or settings.lm_studio_model_name
        self.temperature = temperature or settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.timeout = settings.llm_request_timeout

        self._llm: Optional[ChatOpenAI] = None

        logger.info(
            f"Initialized LLM service with base_url={self.base_url}, "
            f"model={self.model_name}"
        )

    @property
    def llm(self) -> ChatOpenAI:
        """
        Get or create LLM instance.

        Returns:
            ChatOpenAI instance configured for LM Studio
        """
        if self._llm is None:
            try:
                self._llm = ChatOpenAI(
                    base_url=self.base_url,
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                    api_key="not-needed",  # LM Studio doesn't require API key
                )
                logger.debug("Created new ChatOpenAI instance")
            except Exception as e:
                logger.error(f"Failed to create LLM instance: {e}")
                raise LLMError(f"Failed to initialize LLM: {e}") from e

        return self._llm

    def create_llm(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> ChatOpenAI:
        """
        Create a new LLM instance with custom parameters.

        Args:
            temperature: Override temperature
            max_tokens: Override max tokens

        Returns:
            New ChatOpenAI instance
        """
        try:
            return ChatOpenAI(
                base_url=self.base_url,
                model=self.model_name,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                timeout=self.timeout,
                api_key="not-needed",
            )
        except Exception as e:
            logger.error(f"Failed to create custom LLM instance: {e}")
            raise LLMError(f"Failed to create LLM: {e}") from e

    async def test_connection(self) -> bool:
        """
        Test connection to LM Studio.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = await self.llm.ainvoke("Hello")
            logger.info("LM Studio connection test successful")
            return True
        except Exception as e:
            logger.error(f"LM Studio connection test failed: {e}")
            return False


def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    return LLMService()
