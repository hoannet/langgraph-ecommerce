"""Pydantic schemas for data validation."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from src.models.enums import IntentType, MessageRole, PaymentStatus


class ChatMessage(BaseModel):
    """Chat message schema."""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntentClassification(BaseModel):
    """Intent classification result."""

    intent: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class PaymentRequest(BaseModel):
    """Payment request schema."""

    amount: float = Field(gt=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaymentResponse(BaseModel):
    """Payment response schema."""

    transaction_id: str
    status: PaymentStatus
    amount: float
    currency: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request schema for API."""

    message: str
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Chat response schema for API."""

    message: str
    session_id: str
    intent: Optional[IntentType] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
