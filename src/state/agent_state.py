"""Agent state models."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from src.models.enums import AgentType


class AgentMetadata(BaseModel):
    """Metadata for agent execution."""

    agent_type: AgentType
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """State for individual agent."""

    agent_type: AgentType
    is_active: bool = True
    metadata: AgentMetadata
    config: Dict[str, Any] = Field(default_factory=dict)
