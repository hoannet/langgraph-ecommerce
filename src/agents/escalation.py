"""Escalation agent for handling complex cases."""

from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage

from src.agents.base import BaseAgent
from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType
from src.prompts.agent_prompts import ESCALATION_PROMPT
from src.services.llm_service import LLMService

logger = get_logger(__name__)


class EscalationAgent(BaseAgent):
    """Agent for escalating complex cases to human support."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize escalation agent.

        Args:
            llm_service: LLM service instance
            config: Agent configuration
        """
        super().__init__(
            agent_type=AgentType.ESCALATION,
            llm_service=llm_service,
            config=config,
        )

    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process escalation case.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            Escalation response
        """
        if not messages:
            raise AgentError("No messages provided for escalation")

        try:
            # Get the last user message
            user_message = messages[-1].content

            # Prepare context summary
            context_summary = self._prepare_context_summary(messages, context)

            # Create prompt
            prompt = ESCALATION_PROMPT.format_messages(
                system_prompt=self.system_prompt,
                chat_history=messages[:-1] if len(messages) > 1 else [],
                user_message=user_message,
                context=context_summary,
            )

            # Get LLM response
            response = await self.llm.ainvoke(prompt)
            result = response.content

            logger.info("Generated escalation response")
            return result

        except Exception as e:
            logger.error(f"Escalation processing failed: {e}")
            return (
                "I understand you need additional assistance. "
                "I'm connecting you with our support team who will help you shortly. "
                "Please hold on."
            )

    def _prepare_context_summary(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """
        Prepare context summary for escalation.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            Context summary string
        """
        summary_parts = [f"Conversation length: {len(messages)} messages"]

        if context:
            if "intent" in context:
                summary_parts.append(f"Detected intent: {context['intent']}")
            if "payment_data" in context:
                summary_parts.append("Payment-related issue")

        return "; ".join(summary_parts)
