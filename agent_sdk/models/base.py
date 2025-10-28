"""Base models for all agents."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, ConfigDict


class BaseModel(PydanticBaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )


class EventType(str, Enum):
    """Standard event types across the system."""

    # Aletheia events
    CONTENT_INGESTED = "content.ingested"
    IDEA_CREATED = "idea.created"
    IDEA_SCORED = "idea.scored"

    # IRIS events
    OUTLINE_READY = "outline.ready"
    DRAFT_GENERATED = "draft.generated"

    # Erebus events
    DRAFT_CLEANED = "draft.cleaned"

    # Kairos events
    PUBLISH_SCHEDULED = "publish.scheduled"
    PUBLISH_COMPLETED = "publish.completed"
    PUBLISH_FAILED = "publish.failed"

    # Mnemosyne events
    CONTENT_LEARNED = "content.learned"
    CONTEXT_RETRIEVED = "context.retrieved"


class EventEnvelope(BaseModel):
    """
    Standard event envelope for inter-agent communication.

    All agents use this format for publishing events to the message bus.
    """

    type: EventType = Field(..., description="Type of event")
    id: UUID = Field(default_factory=uuid4, description="Unique event ID")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event creation time (UTC)"
    )
    actor: str = Field(..., description="Agent that generated this event")
    data_ref: Optional[str] = Field(
        None, description="Reference to data (S3 URI, database ID, etc.)"
    )
    meta: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    correlation_id: Optional[UUID] = Field(
        None, description="ID to correlate related events"
    )

    def model_dump_json_str(self) -> str:
        """Serialize to JSON string for message queue."""
        return self.model_dump_json()

    @classmethod
    def from_json_str(cls, json_str: str) -> "EventEnvelope":
        """Deserialize from JSON string."""
        return cls.model_validate_json(json_str)


class AgentStatus(str, Enum):
    """Standard agent health statuses."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck(BaseModel):
    """Standard health check response."""

    status: AgentStatus = Field(..., description="Current agent status")
    agent: str = Field(..., description="Agent name")
    version: str = Field(default="0.1.0", description="Agent version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Check timestamp"
    )
    details: dict[str, Any] = Field(
        default_factory=dict, description="Additional health details"
    )
