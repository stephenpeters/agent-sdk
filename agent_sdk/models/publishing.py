"""Publishing models for Kairos agent."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field, HttpUrl

from agent_sdk.models.base import BaseModel


class Platform(str, Enum):
    """Supported publishing platforms."""

    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    MEDIUM = "medium"
    NOTION = "notion"


class PublishStatus(str, Enum):
    """Publication lifecycle status."""

    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EngagementMetrics(BaseModel):
    """Engagement metrics for published content."""

    views: int = Field(default=0, ge=0, description="Total views/impressions")
    likes: int = Field(default=0, ge=0, description="Total likes/reactions")
    comments: int = Field(default=0, ge=0, description="Total comments")
    shares: int = Field(default=0, ge=0, description="Total shares/reposts")
    clicks: int = Field(default=0, ge=0, description="Total link clicks")

    engagement_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Overall engagement rate"
    )

    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="Last metrics update"
    )

    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate based on interactions."""
        if self.views == 0:
            return 0.0
        interactions = self.likes + self.comments + self.shares + self.clicks
        return interactions / self.views


class PublishModel(BaseModel):
    """Publication record managed by Kairos."""

    id: UUID = Field(default_factory=uuid4, description="Unique publication ID")
    content_id: UUID = Field(..., description="Associated cleaned content ID")
    draft_id: UUID = Field(..., description="Original draft ID")
    idea_id: UUID = Field(..., description="Original idea ID")

    # Content
    title: str = Field(..., min_length=1, max_length=500, description="Post title")
    content: str = Field(..., min_length=1, description="Final content to publish")

    # Platform configuration
    platform: Platform = Field(..., description="Target publishing platform")
    platform_post_id: Optional[str] = Field(
        None, description="Platform-specific post ID after publishing"
    )
    platform_url: Optional[HttpUrl] = Field(
        None, description="Public URL of published post"
    )

    # Scheduling
    scheduled_time: Optional[datetime] = Field(
        None, description="Scheduled publication time (UTC)"
    )
    published_at: Optional[datetime] = Field(
        None, description="Actual publication time (UTC)"
    )

    # Status tracking
    status: PublishStatus = Field(
        default=PublishStatus.PENDING_APPROVAL, description="Current status"
    )
    approval_notes: Optional[str] = Field(
        None, description="Notes from approval process"
    )

    # Engagement
    metrics: Optional[EngagementMetrics] = Field(
        None, description="Engagement metrics (populated post-publish)"
    )

    # Error handling
    error_message: Optional[str] = Field(
        None, description="Error message if publishing failed"
    )
    retry_count: int = Field(default=0, ge=0, description="Number of publish retry attempts")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    def approve(self, notes: Optional[str] = None) -> None:
        """Approve content for publication."""
        self.status = PublishStatus.APPROVED
        self.approval_notes = notes
        self.updated_at = datetime.utcnow()

    def schedule(self, scheduled_time: datetime) -> None:
        """Schedule content for future publication."""
        self.scheduled_time = scheduled_time
        self.status = PublishStatus.SCHEDULED
        self.updated_at = datetime.utcnow()

    def mark_publishing(self) -> None:
        """Mark as currently publishing."""
        self.status = PublishStatus.PUBLISHING
        self.updated_at = datetime.utcnow()

    def mark_published(self, platform_post_id: str, platform_url: str) -> None:
        """Mark as successfully published."""
        self.status = PublishStatus.PUBLISHED
        self.platform_post_id = platform_post_id
        self.platform_url = platform_url
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        """Mark as failed with error message."""
        self.status = PublishStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel scheduled publication."""
        self.status = PublishStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def is_ready_to_publish(self) -> bool:
        """Check if content is ready for publication."""
        if self.status == PublishStatus.SCHEDULED:
            if self.scheduled_time:
                return datetime.utcnow() >= self.scheduled_time
        return self.status == PublishStatus.APPROVED

    def update_metrics(self, metrics: EngagementMetrics) -> None:
        """Update engagement metrics."""
        self.metrics = metrics
        self.updated_at = datetime.utcnow()
