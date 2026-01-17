"""Unit tests for agents."""

import pytest
from langchain_core.messages import HumanMessage

from src.agents.conversation import ConversationAgent
from src.agents.intent_classifier import IntentClassifierAgent
from src.models.enums import IntentType


class TestIntentClassifierAgent:
    """Tests for IntentClassifierAgent."""

    @pytest.mark.asyncio
    async def test_classify_payment_intent(self, llm_service):
        """Test payment intent classification."""
        agent = IntentClassifierAgent(llm_service=llm_service)
        messages = [HumanMessage(content="I want to make a payment of $100")]

        # Note: This test requires LM Studio to be running
        # In real tests, you would mock the LLM response
        # result = await agent.classify(messages)
        # assert result.intent == IntentType.PAYMENT

    def test_agent_initialization(self, llm_service):
        """Test agent initialization."""
        agent = IntentClassifierAgent(llm_service=llm_service)
        assert agent.agent_type.value == "intent_classifier"


class TestConversationAgent:
    """Tests for ConversationAgent."""

    def test_agent_initialization(self, llm_service):
        """Test agent initialization."""
        agent = ConversationAgent(llm_service=llm_service)
        assert agent.agent_type.value == "conversation"
