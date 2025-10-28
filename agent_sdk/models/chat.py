"""Chat and conversation models for Aletheia."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class FeedbackType(str, Enum):
    """Type of feedback on an idea or suggestion."""

    ACCEPT = "accept"
    REJECT = "reject"
    FLAG = "flag"  # flag for later review


class ChatMessage(BaseModel):
    """Individual message in a conversation."""

    id: UUID = Field(default_factory=uuid4, description="Unique message ID")
    session_id: UUID = Field(..., description="Session this message belongs to")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (tokens, model, latency, etc.)",
    )

    # Optional references to generated ideas
    idea_refs: list[UUID] = Field(
        default_factory=list, description="IDs of ideas referenced or generated"
    )

    # Context confidence at time of message
    context_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence in context at message time"
    )


class ChatSession(BaseModel):
    """Conversation session with context tracking."""

    id: UUID = Field(default_factory=uuid4, description="Unique session ID")
    user_id: Optional[str] = Field(None, description="User identifier (optional for MVP)")
    title: Optional[str] = Field(None, description="Session title or summary")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = Field(None, description="Timestamp of last message")

    # Context tracking
    topics: list[str] = Field(
        default_factory=list, description="Topics discussed in this session"
    )
    topic_weights: dict[str, float] = Field(
        default_factory=dict, description="Weight/relevance of each topic"
    )

    # Session metadata
    message_count: int = Field(0, description="Total messages in session")
    ideas_generated: int = Field(0, description="Ideas generated in this session")
    ideas_accepted: int = Field(0, description="Ideas accepted by user")
    ideas_rejected: int = Field(0, description="Ideas rejected by user")

    # Memory integration
    mnemosyne_sync_at: Optional[datetime] = Field(
        None, description="Last sync with Mnemosyne"
    )
    context_confidence: float = Field(
        0.8, ge=0.0, le=1.0, description="Current context confidence score"
    )

    # Session state
    is_active: bool = Field(True, description="Whether session is active")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        """Update session timestamps."""
        self.updated_at = datetime.utcnow()
        self.last_message_at = datetime.utcnow()

    def add_topic(self, topic: str, weight: float = 1.0) -> None:
        """Add or update topic weight."""
        if topic not in self.topics:
            self.topics.append(topic)
        self.topic_weights[topic] = weight

    def increment_message_count(self) -> None:
        """Increment message count and touch session."""
        self.message_count += 1
        self.touch()

    def record_idea(self, accepted: Optional[bool] = None) -> None:
        """Record an idea generation and optional feedback."""
        self.ideas_generated += 1
        if accepted is True:
            self.ideas_accepted += 1
        elif accepted is False:
            self.ideas_rejected += 1
        self.touch()


class ChatRequest(BaseModel):
    """Request to send a message to Aletheia."""

    session_id: Optional[UUID] = Field(None, description="Session ID (null to create new)")
    message: str = Field(..., min_length=1, description="User message")
    context_window: int = Field(
        10, ge=1, le=50, description="Number of previous messages to include"
    )
    topics: list[str] = Field(
        default_factory=list, description="Explicit topics to focus on"
    )
    include_ideas: bool = Field(
        True, description="Whether to search for and suggest ideas"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class IdeaSuggestion(BaseModel):
    """An idea suggested by Aletheia during conversation."""

    idea_id: UUID = Field(..., description="Reference to IdeaModel")
    title: str = Field(..., description="Idea title")
    summary: str = Field(..., description="Brief summary")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance to conversation")
    source: Optional[str] = Field(None, description="Source of the idea")


class ChatResponse(BaseModel):
    """Response from Aletheia chat."""

    session_id: UUID = Field(..., description="Session ID")
    message_id: UUID = Field(..., description="ID of assistant's message")
    content: str = Field(..., description="Assistant's response")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Suggested ideas
    ideas: list[IdeaSuggestion] = Field(
        default_factory=list, description="Ideas suggested in response"
    )

    # Context information
    topics_discussed: list[str] = Field(
        default_factory=list, description="Topics identified in this exchange"
    )
    context_confidence: float = Field(
        0.8, ge=0.0, le=1.0, description="Confidence in current context"
    )
    mnemosyne_available: bool = Field(
        True, description="Whether Mnemosyne was available for this response"
    )

    # Performance metrics
    latency_ms: Optional[int] = Field(None, description="Response generation time in ms")
    tokens_used: Optional[int] = Field(None, description="Tokens used for generation")

    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackRequest(BaseModel):
    """User feedback on an idea or suggestion."""

    session_id: UUID = Field(..., description="Session ID")
    idea_id: UUID = Field(..., description="ID of the idea")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    comment: Optional[str] = Field(None, description="Optional comment from user")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeedbackResponse(BaseModel):
    """Response to feedback submission."""

    success: bool = Field(..., description="Whether feedback was recorded")
    message: str = Field(..., description="Status message")
    updated_context_confidence: Optional[float] = Field(
        None, description="Updated context confidence after feedback"
    )


class SessionListResponse(BaseModel):
    """List of chat sessions."""

    sessions: list[ChatSession] = Field(..., description="List of sessions")
    total: int = Field(..., description="Total number of sessions")
    active_count: int = Field(0, description="Number of active sessions")


class SessionHistoryResponse(BaseModel):
    """Full history of a chat session."""

    session: ChatSession = Field(..., description="Session metadata")
    messages: list[ChatMessage] = Field(..., description="All messages in session")
    ideas_referenced: list[UUID] = Field(
        default_factory=list, description="All idea IDs referenced in session"
    )


class ConversationSummary(BaseModel):
    """Summary of a completed or ongoing conversation."""

    session_id: UUID = Field(..., description="Session ID")
    summary: str = Field(..., description="Textual summary of conversation")
    key_topics: list[str] = Field(..., description="Main topics discussed")
    insights: list[str] = Field(
        default_factory=list, description="Key insights or patterns identified"
    )
    ideas_generated: int = Field(0, description="Total ideas generated")
    ideas_accepted: int = Field(0, description="Ideas accepted by user")
    created_at: datetime = Field(..., description="When session started")
    duration_minutes: Optional[int] = Field(None, description="Session duration")
    metadata: dict[str, Any] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    """Chunk of a streaming response."""

    session_id: UUID = Field(..., description="Session ID")
    message_id: UUID = Field(..., description="Message ID being streamed")
    chunk: str = Field(..., description="Text chunk")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    metadata: dict[str, Any] = Field(default_factory=dict)
