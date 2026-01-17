"""FAQ agent for answering common questions."""

from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage

from src.agents.base import BaseAgent
from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType
from src.prompts.agent_prompts import FAQ_PROMPT
from src.services.llm_service import LLMService

logger = get_logger(__name__)


class FAQAgent(BaseAgent):
    """Agent for answering frequently asked questions."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize FAQ agent.

        Args:
            llm_service: LLM service instance
            config: Agent configuration
        """
        super().__init__(
            agent_type=AgentType.FAQ,
            llm_service=llm_service,
            config=config,
        )

    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process FAQ question and generate answer.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            FAQ answer
        """
        if not messages:
            raise AgentError("No messages provided for FAQ")

        try:
            # Get the last user message as the question
            question = messages[-1].content

            # Create prompt
            prompt = FAQ_PROMPT.format_messages(
                system_prompt=self.system_prompt,
                chat_history=messages[:-1] if len(messages) > 1 else [],
                question=question,
            )

            # Get LLM response
            response = await self.llm.ainvoke(prompt)
            result = response.content

            logger.info("Generated FAQ response")
            return result

        except Exception as e:
            logger.error(f"FAQ processing failed: {e}")
            return (
                "I apologize, but I'm having trouble answering your question right now. "
                "Please try rephrasing or contact our support team for assistance."
            )
