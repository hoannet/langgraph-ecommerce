"""Conversation memory management."""

from typing import List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class ConversationMemory:
    """Manages conversation history with sliding window and summarization."""

    def __init__(
        self,
        max_history: Optional[int] = None,
        summary_threshold: Optional[int] = None,
    ) -> None:
        """
        Initialize conversation memory.

        Args:
            max_history: Maximum number of messages to keep
            summary_threshold: Threshold for triggering summarization
        """
        settings = get_settings()
        self.max_history = max_history or settings.max_conversation_history
        self.summary_threshold = (
            summary_threshold or settings.conversation_summary_threshold
        )
        self.messages: List[BaseMessage] = []
        self.summary: Optional[str] = None

        logger.debug(
            f"Initialized ConversationMemory with max_history={self.max_history}"
        )

    def add_message(self, message: BaseMessage) -> None:
        """
        Add a message to conversation history.

        Args:
            message: Message to add
        """
        self.messages.append(message)
        logger.debug(f"Added message: {message.type}")

        # Trim if exceeds max history
        if len(self.messages) > self.max_history:
            self._trim_history()

    def add_user_message(self, content: str) -> None:
        """Add a user message."""
        self.add_message(HumanMessage(content=content))

    def add_ai_message(self, content: str) -> None:
        """Add an AI message."""
        self.add_message(AIMessage(content=content))

    def add_system_message(self, content: str) -> None:
        """Add a system message."""
        self.add_message(SystemMessage(content=content))

    def get_messages(self, limit: Optional[int] = None) -> List[BaseMessage]:
        """
        Get conversation messages.

        Args:
            limit: Optional limit on number of messages

        Returns:
            List of messages
        """
        if limit:
            return self.messages[-limit:]
        return self.messages.copy()

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages.clear()
        self.summary = None
        logger.debug("Cleared conversation history")

    def _trim_history(self) -> None:
        """Trim conversation history to max length."""
        if len(self.messages) > self.max_history:
            # Keep the most recent messages
            removed_count = len(self.messages) - self.max_history
            self.messages = self.messages[-self.max_history :]
            logger.debug(f"Trimmed {removed_count} messages from history")

    def get_context_summary(self) -> str:
        """
        Get a summary of the conversation context.

        Returns:
            Context summary string
        """
        if not self.messages:
            return "No conversation history."

        message_count = len(self.messages)
        user_messages = sum(1 for m in self.messages if isinstance(m, HumanMessage))
        ai_messages = sum(1 for m in self.messages if isinstance(m, AIMessage))

        return (
            f"Conversation has {message_count} messages "
            f"({user_messages} from user, {ai_messages} from assistant)"
        )


class SessionMemoryManager:
    """Manages memory for multiple conversation sessions."""

    def __init__(self) -> None:
        """Initialize session memory manager."""
        self.sessions: dict[str, ConversationMemory] = {}
        logger.debug("Initialized SessionMemoryManager")

    def get_session(self, session_id: str) -> ConversationMemory:
        """
        Get or create conversation memory for a session.

        Args:
            session_id: Session identifier

        Returns:
            ConversationMemory instance
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory()
            logger.debug(f"Created new session: {session_id}")

        return self.sessions[session_id]

    def clear_session(self, session_id: str) -> None:
        """
        Clear a session's memory.

        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            self.sessions[session_id].clear()
            logger.debug(f"Cleared session: {session_id}")

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.debug(f"Deleted session: {session_id}")
