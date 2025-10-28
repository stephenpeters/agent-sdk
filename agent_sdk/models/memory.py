"""Memory and context models for Mnemosyne system."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryTier(str, Enum):
    """Memory tier classification."""

    SHORT_TERM = "short_term"  # ≤30 days (Aletheia cache)
    MID_TERM = "mid_term"  # 30-90 days (Aletheia summaries)
    LONG_TERM = "long_term"  # Indefinite (Mnemosyne archive)


class ContextDepth(str, Enum):
    """Query depth level."""

    SUMMARY = "summary"
    DETAILED = "detailed"


class ContextSource(str, Enum):
    """Source of context information."""

    USER_COMMENTS = "user_comments"
    AGENT_OUTPUTS = "agent_outputs"
    DOCUMENTS = "documents"


class ContextSummary(BaseModel):
    """Context summary with embedding reference."""

    id: UUID = Field(default_factory=uuid4, description="Unique summary ID")
    topic: str = Field(..., description="Topic or theme of summary")
    summary: str = Field(..., description="Summary text")
    weight: float = Field(..., ge=0.0, le=1.0, description="Relevance weight")
    embedding_id: Optional[str] = Field(None, description="Reference to embedding vector")
    tier: MemoryTier = Field(..., description="Memory tier classification")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if summary has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def touch(self) -> None:
        """Update accessed_at timestamp (reinforcement)."""
        self.accessed_at = datetime.utcnow()

    def calculate_age_days(self) -> int:
        """Calculate age in days."""
        return (datetime.utcnow() - self.created_at).days


class ContextDetail(BaseModel):
    """Detailed context record."""

    timestamp: datetime = Field(..., description="When this context was recorded")
    source_agent: str = Field(..., description="Agent that generated this context")
    excerpt: str = Field(..., description="Context excerpt or detail")
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryFilters(BaseModel):
    """Filters for context queries."""

    source: Optional[ContextSource] = Field(None, description="Filter by source type")
    include_metadata: bool = Field(True, description="Include metadata in response")
    min_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Minimum confidence score")


class QueryRequest(BaseModel):
    """Request for querying Mnemosyne context."""

    agent: str = Field(..., description="Agent making the request")
    topic: str = Field(..., description="Primary keyword or ontology path")
    range: Optional[str] = Field(
        None, description="Date range filter (e.g., '2025-07-01 to 2025-10-01')"
    )
    time_window_days: Optional[int] = Field(90, ge=1, description="Time window in days")
    depth: ContextDepth = Field(
        ContextDepth.SUMMARY, description="Query depth (summary or detailed)"
    )
    topics: list[str] = Field(default_factory=list, description="Additional related topics")
    filters: QueryFilters = Field(default_factory=QueryFilters)


class QueryMetadata(BaseModel):
    """Metadata for query response."""

    retrieved: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    last_updated: datetime = Field(..., description="When this context was last updated")
    source_count: int = Field(0, description="Number of source records")


class QueryResponse(BaseModel):
    """Response from Mnemosyne context query."""

    topic: str = Field(..., description="Topic queried")
    summary: str = Field(..., description="Summary of context")
    context_summaries: list[ContextSummary] = Field(
        default_factory=list, description="Context summary objects"
    )
    details: list[ContextDetail] = Field(
        default_factory=list, description="Detailed context records"
    )
    metadata: QueryMetadata = Field(..., description="Query metadata")


class ContextUpdate(BaseModel):
    """Update to push to Mnemosyne."""

    session_id: UUID = Field(..., description="Session identifier")
    agent: str = Field(..., description="Agent pushing the update")
    accepted_ideas: list[str] = Field(default_factory=list, description="Accepted idea IDs")
    rejected_ideas: list[str] = Field(default_factory=list, description="Rejected idea IDs")
    summary_text: str = Field(..., description="Session summary text")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CacheEntry(BaseModel):
    """Entry in Aletheia's short-term cache."""

    id: UUID = Field(default_factory=uuid4)
    content: str = Field(..., description="Cached content")
    embedding: Optional[list[float]] = Field(None, description="Embedding vector")
    topic: str = Field(..., description="Associated topic")
    tier: MemoryTier = Field(MemoryTier.SHORT_TERM)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(0, description="Number of times accessed")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        """Update access tracking."""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1

    def calculate_relevance_score(self, query_embedding: list[float]) -> float:
        """
        Calculate cosine similarity with query embedding.

        Args:
            query_embedding: Query vector to compare against

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if self.embedding is None or not query_embedding:
            return 0.0

        # Cosine similarity calculation
        dot_product = sum(a * b for a, b in zip(self.embedding, query_embedding))
        magnitude_a = sum(a * a for a in self.embedding) ** 0.5
        magnitude_b = sum(b * b for b in query_embedding) ** 0.5

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    def should_prune(self, threshold: float = 0.5, max_age_days: int = 30) -> bool:
        """
        Determine if entry should be pruned.

        Args:
            threshold: Minimum relevance threshold
            max_age_days: Maximum age in days

        Returns:
            True if entry should be pruned
        """
        age_days = (datetime.utcnow() - self.created_at).days
        return age_days > max_age_days


class RefreshStatus(BaseModel):
    """Status of daily refresh cycle."""

    started_at: datetime = Field(..., description="When refresh started")
    completed_at: Optional[datetime] = Field(None, description="When refresh completed")
    success: bool = Field(False, description="Whether refresh succeeded")
    mnemosyne_available: bool = Field(False, description="Whether Mnemosyne API was available")
    context_confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="Confidence in current context"
    )
    entries_pruned: int = Field(0, description="Number of entries pruned")
    summaries_created: int = Field(0, description="Number of summaries created")
    updates_pushed: int = Field(0, description="Number of updates pushed to Mnemosyne")
    errors: list[str] = Field(default_factory=list, description="Errors encountered")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def mark_complete(self, success: bool = True) -> None:
        """Mark refresh as complete."""
        self.completed_at = datetime.utcnow()
        self.success = success

    def add_error(self, error: str) -> None:
        """Add error to list."""
        self.errors.append(error)
        self.success = False
