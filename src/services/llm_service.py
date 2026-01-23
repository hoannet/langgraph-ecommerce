"""LLM service for multiple LLM provider integration."""

from typing import Optional, Union

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.config import get_settings
from src.core.exceptions import LLMError
from src.core.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for managing LLM interactions with multiple providers."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        """
        Initialize LLM service.

        Args:
            provider: LLM provider ('lm_studio', 'gemini', or 'openai')
            model_name: Model name
            temperature: Temperature setting
            max_tokens: Maximum tokens
        """
        settings = get_settings()

        self.provider = provider or settings.llm_provider
        self.temperature = temperature or settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.timeout = settings.llm_request_timeout

        # Provider-specific settings
        if self.provider == "gemini":
            self.model_name = model_name or settings.gemini_model_name
            self.api_key = settings.gemini_api_key
            if not self.api_key:
                raise LLMError("Gemini API key not configured. Set GEMINI_API_KEY in .env")
        elif self.provider == "openai":
            self.model_name = model_name or settings.openai_model_name
            self.api_key = settings.openai_api_key
            if not self.api_key:
                raise LLMError("OpenAI API key not configured. Set OPENAI_API_KEY in .env")
        else:  # lm_studio
            self.model_name = model_name or settings.lm_studio_model_name
            self.base_url = settings.lm_studio_base_url
            self.api_key = settings.lm_studio_api_key

        self._llm: Optional[Union[ChatOpenAI, ChatGoogleGenerativeAI]] = None

        logger.info(
            f"Initialized LLM service with provider={self.provider}, "
            f"model={self.model_name}"
        )

    @property
    def llm(self) -> Union[ChatOpenAI, ChatGoogleGenerativeAI]:
        """
        Get or create LLM instance.

        Returns:
            LLM instance (ChatOpenAI or ChatGoogleGenerativeAI)
        """
        if self._llm is None:
            try:
                if self.provider == "gemini":
                    self._llm = ChatGoogleGenerativeAI(
                        model=self.model_name,
                        google_api_key=self.api_key,
                        temperature=self.temperature,
                        max_output_tokens=self.max_tokens,
                        timeout=self.timeout,
                    )
                    logger.debug(f"Created Gemini instance: {self.model_name}")
                elif self.provider == "openai":
                    self._llm = ChatOpenAI(
                        model=self.model_name,
                        api_key=self.api_key,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        timeout=self.timeout,
                    )
                    logger.debug(f"Created OpenAI instance: {self.model_name}")
                else:  # lm_studio
                    self._llm = ChatOpenAI(
                        base_url=self.base_url,
                        model=self.model_name,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        timeout=self.timeout,
                        api_key=self.api_key,
                    )
                    logger.debug(f"Created LM Studio instance: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to create LLM instance: {e}")
                raise LLMError(f"Failed to initialize {self.provider} LLM: {e}") from e

        return self._llm

    def create_llm(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Union[ChatOpenAI, ChatGoogleGenerativeAI]:
        """
        Create a new LLM instance with custom parameters.

        Args:
            temperature: Override temperature
            max_tokens: Override max tokens

        Returns:
            New LLM instance
        """
        try:
            if self.provider == "gemini":
                return ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=temperature or self.temperature,
                    max_output_tokens=max_tokens or self.max_tokens,
                    timeout=self.timeout,
                )
            elif self.provider == "openai":
                return ChatOpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                    timeout=self.timeout,
                )
            else:  # lm_studio
                return ChatOpenAI(
                    base_url=self.base_url,
                    model=self.model_name,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                    timeout=self.timeout,
                    api_key=self.api_key,
                )
        except Exception as e:
            logger.error(f"Failed to create custom LLM instance: {e}")
            raise LLMError(f"Failed to create {self.provider} LLM: {e}") from e

    async def test_connection(self) -> bool:
        """
        Test connection to LLM provider.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = await self.llm.ainvoke("Hello")
            logger.info(f"{self.provider} connection test successful")
            return True
        except Exception as e:
            logger.error(f"{self.provider} connection test failed: {e}")
            return False


def get_llm_service(provider: Optional[str] = None) -> LLMService:
    """
    Get LLM service instance.
    
    Args:
        provider: Optional provider override ('lm_studio' or 'gemini')
    
    Returns:
        LLMService instance
    """
    return LLMService(provider=provider)

