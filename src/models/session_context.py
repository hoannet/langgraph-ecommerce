"""Session context models for conversation state management."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ConversationState(str, Enum):
    """Conversation state enum."""

    BROWSING = "browsing"  # User is browsing products
    SELECTED = "selected"  # User selected a product
    ORDERED = "ordered"  # Order created, pending payment
    PAYING = "paying"  # Payment in progress
    COMPLETED = "completed"  # Transaction completed


class SessionContext(BaseModel):
    """Session context for maintaining conversation state."""

    session_id: str = Field(description="Unique session identifier")
    
    # Product browsing context
    last_viewed_products: List[dict] = Field(
        default_factory=list,
        description="Products from most recent search",
    )
    
    # Selection context
    selected_product_id: Optional[str] = Field(
        default=None,
        description="Currently selected product ID",
    )
    
    # Order context
    pending_order_id: Optional[str] = Field(
        default=None,
        description="ID of order awaiting payment",
    )
    
    # State tracking
    conversation_state: ConversationState = Field(
        default=ConversationState.BROWSING,
        description="Current conversation state",
    )
    
    # Metadata
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Last context update timestamp",
    )
    
    def clear_product_context(self) -> None:
        """Clear product-related context."""
        self.last_viewed_products = []
        self.selected_product_id = None
    
    def clear_order_context(self) -> None:
        """Clear order-related context."""
        self.pending_order_id = None
    
    def reset(self) -> None:
        """Reset all context to initial state."""
        self.last_viewed_products = []
        self.selected_product_id = None
        self.pending_order_id = None
        self.conversation_state = ConversationState.BROWSING
        self.last_updated = datetime.now()
