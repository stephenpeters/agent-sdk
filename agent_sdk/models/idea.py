"""Idea models for Aletheia agent."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field, HttpUrl

from agent_sdk.models.base import BaseModel


class SourceType(str, Enum):
    """Content source types supported by Aletheia."""

    URL = "url"
    RSS = "rss"
    PDF = "pdf"
    YOUTUBE = "youtube"
    MANUAL = "manual"


class IdeaStatus(str, Enum):
    """Lifecycle status of an idea."""

    PROCESSING = "processing"
    SCORED = "scored"
    APPROVED = "approved"
    REJECTED = "rejected"
    DRAFTED = "drafted"


class IdeaScore(BaseModel):
    """Scoring metrics for an idea."""

    novelty: float = Field(..., ge=0.0, le=1.0, description="Novelty score (0-1)")
    topicality: float = Field(..., ge=0.0, le=1.0, description="Topicality/trending score (0-1)")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance to configured topics (0-1)")
    overall: float = Field(..., ge=0.0, le=1.0, description="Overall weighted score (0-1)")

    def calculate_overall(
        self,
        novelty_weight: float = 0.4,
        topicality_weight: float = 0.3,
        relevance_weight: float = 0.3,
    ) -> float:
        """Calculate overall score from components."""
        return (
            self.novelty * novelty_weight
            + self.topicality * topicality_weight
            + self.relevance * relevance_weight
        )


class IdeaModel(BaseModel):
    """Content idea discovered and scored by Aletheia."""

    id: UUID = Field(default_factory=uuid4, description="Unique idea ID")
    title: str = Field(..., min_length=1, max_length=500, description="Idea title")
    summary: str = Field(..., min_length=1, description="Brief summary of the idea")
    content: Optional[str] = Field(None, description="Full content if available")

    # Source information
    source_type: SourceType = Field(..., description="Type of content source")
    source_url: Optional[HttpUrl] = Field(None, description="Original content URL")
    source_metadata: dict[str, str] = Field(
        default_factory=dict, description="Additional source metadata"
    )

    # Scoring
    score: Optional[IdeaScore] = Field(None, description="Idea scoring metrics")

    # Categorization
    topics: list[str] = Field(default_factory=list, description="Identified topic tags")
    keywords: list[str] = Field(default_factory=list, description="Extracted keywords")

    # Lifecycle
    status: IdeaStatus = Field(
        default=IdeaStatus.PROCESSING, description="Current idea status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    # Related content
    related_ideas: list[UUID] = Field(
        default_factory=list, description="IDs of related ideas"
    )

    def is_above_threshold(self, threshold: float = 0.65) -> bool:
        """Check if idea meets minimum score threshold."""
        if not self.score:
            return False
        return self.score.overall >= threshold

    def approve(self) -> None:
        """Mark idea as approved."""
        self.status = IdeaStatus.APPROVED
        self.updated_at = datetime.utcnow()

    def reject(self) -> None:
        """Mark idea as rejected."""
        self.status = IdeaStatus.REJECTED
        self.updated_at = datetime.utcnow()
