"""Validation utilities."""

from typing import Any, Dict, List

from src.core.exceptions import ValidationError
from src.models.enums import PaymentStatus


def validate_payment_amount(amount: float) -> None:
    """
    Validate payment amount.

    Args:
        amount: Payment amount

    Raises:
        ValidationError: If amount is invalid
    """
    if amount <= 0:
        raise ValidationError("Payment amount must be greater than 0")
    if amount > 1_000_000:
        raise ValidationError("Payment amount exceeds maximum limit")


def validate_currency(currency: str) -> None:
    """
    Validate currency code.

    Args:
        currency: Currency code

    Raises:
        ValidationError: If currency is invalid
    """
    valid_currencies = ["USD", "EUR", "GBP", "VND"]
    if currency not in valid_currencies:
        raise ValidationError(
            f"Invalid currency: {currency}. Supported: {', '.join(valid_currencies)}"
        )


def validate_payment_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate payment data and return list of errors.

    Args:
        data: Payment data dictionary

    Returns:
        List of validation error messages
    """
    errors = []

    if "amount" not in data:
        errors.append("Missing required field: amount")
    elif not isinstance(data["amount"], (int, float)):
        errors.append("Amount must be a number")
    elif data["amount"] <= 0:
        errors.append("Amount must be greater than 0")

    if "currency" in data:
        valid_currencies = ["USD", "EUR", "GBP", "VND"]
        if data["currency"] not in valid_currencies:
            errors.append(f"Invalid currency. Supported: {', '.join(valid_currencies)}")

    return errors


def validate_message_content(content: str) -> None:
    """
    Validate message content.

    Args:
        content: Message content

    Raises:
        ValidationError: If content is invalid
    """
    if not content or not content.strip():
        raise ValidationError("Message content cannot be empty")
    if len(content) > 10000:
        raise ValidationError("Message content exceeds maximum length")


def validate_session_id(session_id: str) -> None:
    """
    Validate session ID format.

    Args:
        session_id: Session ID

    Raises:
        ValidationError: If session ID is invalid
    """
    if not session_id or not session_id.strip():
        raise ValidationError("Session ID cannot be empty")
    if not session_id.startswith("session_"):
        raise ValidationError("Invalid session ID format")
