"""FastAPI dependencies."""

from typing import Generator

from src.graphs.chat_workflow import get_chat_workflow
from src.memory.conversation import SessionMemoryManager
from src.services.llm_service import LLMService


def get_llm_service() -> LLMService:
    """Get LLM service dependency."""
    return LLMService()


def get_session_manager() -> SessionMemoryManager:
    """Get session memory manager dependency."""
    return SessionMemoryManager()


def get_workflow() -> Generator:
    """Get chat workflow dependency."""
    workflow = get_chat_workflow()
    try:
        yield workflow
    finally:
        pass
