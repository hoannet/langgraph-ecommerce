"""Utility helper functions."""

import uuid
from datetime import datetime
from typing import Any, Dict


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique ID string
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def generate_session_id() -> str:
    """Generate a session ID."""
    return generate_id("session_")


def generate_transaction_id() -> str:
    """Generate a transaction ID."""
    return generate_id("txn_")


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime to ISO string.

    Args:
        dt: Datetime object

    Returns:
        ISO formatted string
    """
    return dt.isoformat()


def serialize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize dictionary for JSON compatibility.

    Args:
        data: Dictionary to serialize

    Returns:
        Serialized dictionary
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = format_timestamp(value)
        elif isinstance(value, dict):
            result[key] = serialize_dict(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result
