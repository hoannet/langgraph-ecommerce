"""Graph state definitions using TypedDict."""

from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage

from src.models.enums import IntentType, PaymentStatus
from src.models.session_context import SessionContext


class ChatState(TypedDict, total=False):
    """State for chat workflow."""

    messages: List[BaseMessage]
    intent: Optional[IntentType]
    intent_confidence: Optional[float]
    context: Dict[str, Any]
    payment_data: Optional[Dict[str, Any]]
    session_id: str
    next_agent: Optional[str]
    final_response: Optional[str]
    session_context: Optional[SessionContext]  # Added for context management


class PaymentState(TypedDict, total=False):
    """State for payment workflow."""

    transaction_id: str
    amount: float
    currency: str
    status: PaymentStatus
    description: Optional[str]
    validation_errors: List[str]
    metadata: Dict[str, Any]
