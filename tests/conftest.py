"""Pytest configuration and fixtures."""

import pytest
from typing import Generator

from src.services.llm_service import LLMService
from src.memory.conversation import ConversationMemory
from src.models.enums import AgentType


@pytest.fixture
def llm_service() -> LLMService:
    """Fixture for LLM service."""
    return LLMService()


@pytest.fixture
def conversation_memory() -> ConversationMemory:
    """Fixture for conversation memory."""
    return ConversationMemory()


@pytest.fixture
def sample_chat_state() -> dict:
    """Fixture for sample chat state."""
    from langchain_core.messages import HumanMessage

    return {
        "messages": [HumanMessage(content="Hello")],
        "session_id": "test_session",
        "context": {},
    }


@pytest.fixture
def sample_payment_data() -> dict:
    """Fixture for sample payment data."""
    return {
        "amount": 100.0,
        "currency": "USD",
        "description": "Test payment",
    }
