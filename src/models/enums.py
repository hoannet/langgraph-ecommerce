"""Enums for the chatbot application."""

from enum import Enum


class MessageRole(str, Enum):
    """Message role types."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IntentType(str, Enum):
    """User intent types."""

    PAYMENT = "payment"
    FAQ = "faq"
    GENERAL = "general"
    ESCALATION = "escalation"
    PRODUCT_SEARCH = "product_search"
    ORDER = "order"
    UNKNOWN = "unknown"


class PaymentStatus(str, Enum):
    """Payment status types."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Agent types."""

    CONVERSATION = "conversation"
    INTENT_CLASSIFIER = "intent_classifier"
    PAYMENT = "payment"
    FAQ = "faq"
    ESCALATION = "escalation"
    PRODUCT_SEARCH = "product_search"
    ORDER = "order"
