"""Custom exceptions for the chatbot application."""


class ChatbotError(Exception):
    """Base exception for chatbot errors."""

    pass


class AgentError(ChatbotError):
    """Exception raised for agent-related errors."""

    pass


class PaymentError(ChatbotError):
    """Exception raised for payment processing errors."""

    pass


class WorkflowError(ChatbotError):
    """Exception raised for workflow execution errors."""

    pass


class LLMError(ChatbotError):
    """Exception raised for LLM service errors."""

    pass


class StateError(ChatbotError):
    """Exception raised for state management errors."""

    pass


class ValidationError(ChatbotError):
    """Exception raised for validation errors."""

    pass


class ConfigurationError(ChatbotError):
    """Exception raised for configuration errors."""

    pass
