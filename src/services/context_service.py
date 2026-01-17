"""Context service for managing session context."""

from datetime import datetime, timedelta
from typing import Dict, Optional

from src.core.logging import get_logger
from src.models.session_context import SessionContext

logger = get_logger(__name__)


class ContextService:
    """Service for managing session context."""

    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize context service.

        Args:
            ttl_minutes: Time-to-live for context in minutes
        """
        self._storage: Dict[str, SessionContext] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        logger.info(f"ContextService initialized with TTL={ttl_minutes}min")

    def get_context(self, session_id: str) -> SessionContext:
        """
        Get context for a session.

        Args:
            session_id: Session identifier

        Returns:
            Session context (creates new if not exists)
        """
        # Clean expired contexts
        self._cleanup_expired()

        # Get or create context
        if session_id not in self._storage:
            logger.info(f"Creating new context for session: {session_id}")
            self._storage[session_id] = SessionContext(session_id=session_id)
        else:
            logger.debug(f"Retrieved context for session: {session_id}")

        return self._storage[session_id]

    def save_context(self, context: SessionContext) -> None:
        """
        Save context for a session.

        Args:
            context: Session context to save
        """
        context.last_updated = datetime.now()
        self._storage[context.session_id] = context
        logger.debug(f"Saved context for session: {context.session_id}")

    def update_context(self, session_id: str, **updates) -> SessionContext:
        """
        Update specific fields in context.

        Args:
            session_id: Session identifier
            **updates: Fields to update

        Returns:
            Updated context
        """
        context = self.get_context(session_id)

        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
                logger.debug(f"Updated {key} for session {session_id}")

        context.last_updated = datetime.now()
        self.save_context(context)
        return context

    def clear_context(self, session_id: str) -> None:
        """
        Clear context for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._storage:
            del self._storage[session_id]
            logger.info(f"Cleared context for session: {session_id}")

    def reset_context(self, session_id: str) -> SessionContext:
        """
        Reset context to initial state.

        Args:
            session_id: Session identifier

        Returns:
            Reset context
        """
        context = self.get_context(session_id)
        context.reset()
        self.save_context(context)
        logger.info(f"Reset context for session: {session_id}")
        return context

    def _cleanup_expired(self) -> None:
        """Remove expired contexts."""
        now = datetime.now()
        expired = [
            sid
            for sid, ctx in self._storage.items()
            if now - ctx.last_updated > self.ttl
        ]

        for sid in expired:
            del self._storage[sid]
            logger.info(f"Removed expired context: {sid}")


# Global instance
_context_service: Optional[ContextService] = None


def get_context_service() -> ContextService:
    """Get global context service instance."""
    global _context_service
    if _context_service is None:
        _context_service = ContextService()
    return _context_service
