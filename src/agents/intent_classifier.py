"""Intent classifier agent."""

import json
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage

from src.agents.base import BaseAgent
from src.core.exceptions import AgentError
from src.core.logging import get_logger
from src.models.enums import AgentType, IntentType
from src.models.schemas import IntentClassification
from src.prompts.agent_prompts import INTENT_CLASSIFICATION_PROMPT
from src.services.llm_service import LLMService

logger = get_logger(__name__)


class IntentClassifierAgent(BaseAgent):
    """Agent for classifying user intent."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize intent classifier agent.

        Args:
            llm_service: LLM service instance
            config: Agent configuration
        """
        super().__init__(
            agent_type=AgentType.INTENT_CLASSIFIER,
            llm_service=llm_service,
            config=config,
        )

    async def process(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process messages and classify intent.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            JSON string with intent classification
        """
        if not messages:
            raise AgentError("No messages provided for intent classification")

        # Get the last user message
        user_message = messages[-1].content
        user_message_lower = user_message.lower()

        # Keyword-based fallback for common patterns (more reliable than LLM)
        # This ensures consistent classification for obvious cases
        if any(keyword in user_message_lower for keyword in ["show me", "search for", "find me", "what products", "do you have", "i want to buy"]):
            if "product" in user_message_lower or any(prod in user_message_lower for prod in ["laptop", "phone", "iphone", "ipad", "book", "shoes", "headphone"]):
                logger.info(f"Keyword match: product_search ('{user_message}')")
                return IntentClassification(
                    intent=IntentType.PRODUCT_SEARCH,
                    confidence=0.95,
                    reasoning="Keyword match: 'show me/search/find' + product name",
                ).model_dump_json()
        
        # Order intent - must come before payment
        if any(keyword in user_message_lower for keyword in ["i want the", "i'll take", "i want that", "i want this", "order the", "buy the"]):
            # Check for selection references
            if any(ref in user_message_lower for ref in ["first", "second", "third", "one", "that", "this", "#1", "#2", "#3"]):
                logger.info(f"Keyword match: order ('{user_message}')")
                return IntentClassification(
                    intent=IntentType.ORDER,
                    confidence=0.95,
                    reasoning="Keyword match: order with selection reference",
                ).model_dump_json()
        
        if "i want product" in user_message_lower or "order product" in user_message_lower:
            logger.info(f"Keyword match: order ('{user_message}')")
            return IntentClassification(
                intent=IntentType.ORDER,
                confidence=0.95,
                reasoning="Keyword match: order request",
            ).model_dump_json()
        
        if any(keyword in user_message_lower for keyword in ["pay now", "i want to pay", "process payment", "make payment", "charge me"]):
            logger.info(f"Keyword match: payment ('{user_message}')")
            return IntentClassification(
                intent=IntentType.PAYMENT,
                confidence=0.95,
                reasoning="Keyword match: payment request",
            ).model_dump_json()

        try:
            # Create prompt
            prompt = INTENT_CLASSIFICATION_PROMPT.format_messages(
                system_prompt=self.system_prompt,
                chat_history=messages[:-1] if len(messages) > 1 else [],
                user_message=user_message,
            )

            # Get LLM response
            response = await self.llm.ainvoke(prompt)
            result = response.content

            logger.info(f"Intent classification result: {result}")
            return result

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            # Return default intent on error
            default_intent = IntentClassification(
                intent=IntentType.GENERAL,
                confidence=0.5,
                reasoning="Classification failed, defaulting to GENERAL",
            )
            return default_intent.model_dump_json()

    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON from LLM response, handling markdown code blocks.

        Args:
            response: Raw LLM response

        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks if present
        response = response.strip()
        
        # Check for ```json ... ``` pattern
        if response.startswith("```json"):
            # Remove ```json from start
            response = response[7:]
            # Remove ``` from end
            if response.endswith("```"):
                response = response[:-3]
        elif response.startswith("```"):
            # Remove ``` from start
            response = response[3:]
            # Remove ``` from end
            if response.endswith("```"):
                response = response[:-3]
        
        return response.strip()

    async def classify(
        self,
        messages: List[BaseMessage],
        context: Optional[Dict[str, Any]] = None,
    ) -> IntentClassification:
        """
        Classify intent and return structured result.

        Args:
            messages: Conversation messages
            context: Additional context

        Returns:
            Intent classification
        """
        result_json = await self.process(messages, context)

        try:
            # Extract JSON from markdown code blocks if present
            cleaned_json = self._extract_json_from_response(result_json)
            
            # Parse JSON response
            result_dict = json.loads(cleaned_json)
            
            # Normalize intent to lowercase (handle both uppercase and lowercase)
            if "intent" in result_dict and isinstance(result_dict["intent"], str):
                result_dict["intent"] = result_dict["intent"].lower()
            
            return IntentClassification(**result_dict)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse intent classification: {e}")
            logger.debug(f"Raw response: {result_json}")
            # Return default
            return IntentClassification(
                intent=IntentType.GENERAL,
                confidence=0.5,
                reasoning="Failed to parse classification result",
            )
