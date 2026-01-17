"""Base agent class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType
from src.prompts.system_prompts import get_system_prompt
from src.services.llm_service import LLMService
from src.state.agent_state import AgentMetadata, AgentState

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(
        self,
        agent_type: AgentType,
        llm_service: Optional[LLMService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize base agent.

        Args:
            agent_type: Type of agent
            llm_service: LLM service instance
            config: Agent configuration
        """
        self.agent_type = agent_type
        self.llm_service = llm_service
        self.config = config or {}
        self.system_prompt = get_system_prompt(agent_type)

        logger.info(f"Initialized {agent_type.value} agent")

    @property
    def llm(self) -> ChatOpenAI:
        """Get LLM instance."""
        if self.llm_service is None:
            raise AgentError("LLM service not configured")
        return self.llm_service.llm

    def get_system_message(self) -> SystemMessage:
        """
        Get system message for this agent.

        Returns:
            System message
        """
        return SystemMessage(content=self.system_prompt)

    @abstractmethod
    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process messages and return response.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            Agent response
        """
        pass

    def create_metadata(
        self,
        execution_time: Optional[float] = None,
        error: Optional[str] = None,
        **kwargs: Any,
    ) -> AgentMetadata:
        """
        Create agent metadata.

        Args:
            execution_time: Execution time in seconds
            error: Error message if any
            **kwargs: Additional metadata

        Returns:
            Agent metadata
        """
        return AgentMetadata(
            agent_type=self.agent_type,
            execution_time=execution_time,
            error=error,
            additional_info=kwargs,
        )

    def create_state(
        self,
        is_active: bool = True,
        metadata: Optional[AgentMetadata] = None,
    ) -> AgentState:
        """
        Create agent state.

        Args:
            is_active: Whether agent is active
            metadata: Agent metadata

        Returns:
            Agent state
        """
        if metadata is None:
            metadata = self.create_metadata()

        return AgentState(
            agent_type=self.agent_type,
            is_active=is_active,
            metadata=metadata,
            config=self.config,
        )
