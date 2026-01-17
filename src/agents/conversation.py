"""Conversation agent for main chat orchestration."""

from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage

from src.agents.base import BaseAgent
from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType
from src.prompts.agent_prompts import CONVERSATION_PROMPT
from src.services.llm_service import LLMService

logger = get_logger(__name__)


class ConversationAgent(BaseAgent):
    """Agent for general conversation and chat orchestration."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize conversation agent.

        Args:
            llm_service: LLM service instance
            config: Agent configuration
        """
        super().__init__(
            agent_type=AgentType.CONVERSATION,
            llm_service=llm_service,
            config=config,
        )

    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process messages and generate response.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            Agent response
        """
        if not messages:
            raise AgentError("No messages provided for conversation")

        try:
            # Get the last user message
            user_message = messages[-1].content

            # Create prompt with chat history
            prompt = CONVERSATION_PROMPT.format_messages(
                system_prompt=self.system_prompt,
                chat_history=messages[:-1] if len(messages) > 1 else [],
                user_message=user_message,
            )

            # Get LLM response
            response = await self.llm.ainvoke(prompt)
            result = response.content

            logger.info("Generated conversation response")
            return result

        except Exception as e:
            logger.error(f"Conversation processing failed: {e}")
            raise AgentError(f"Failed to generate response: {e}") from e
