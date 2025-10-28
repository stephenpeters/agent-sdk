"""Cleaning models for Erebus agent."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field

from agent_sdk.models.base import BaseModel


class CleaningMetrics(BaseModel):
    """Metrics tracking the effectiveness of AI fingerprint removal."""

    ai_likelihood_before: float = Field(..., ge=0.0, le=1.0, description="AI-likelihood before cleaning (0-1)")
    ai_likelihood_after: float = Field(..., ge=0.0, le=1.0, description="AI-likelihood after cleaning (0-1)")
    ai_likelihood_reduction: float = Field(..., description="Percentage point reduction in AI-likelihood")

    voice_deviation_before: float = Field(..., ge=0.0, description="Voice deviation before cleaning")
    voice_deviation_after: float = Field(..., ge=0.0, description="Voice deviation after cleaning")

    edit_distance: int = Field(..., ge=0, description="Levenshtein distance from original")
    edit_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of text modified")
    sentences_modified: int = Field(..., ge=0, description="Number of sentences changed")

    semantic_similarity: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity to original (0-1)")

    iterations: int = Field(..., ge=1, description="Number of cleaning iterations performed")
    processing_time_ms: int = Field(..., ge=0, description="Total processing time in milliseconds")


class DiffEntry(BaseModel):
    """Single difference between original and cleaned text."""

    type: str = Field(..., description="Type of change: 'add', 'remove', 'modify'")
    original: Optional[str] = Field(None, description="Original text segment")
    cleaned: Optional[str] = Field(None, description="Cleaned text segment")
    reason: str = Field(..., description="Reason for this change")
    position: int = Field(..., ge=0, description="Character position in text")


class CleanedContentModel(BaseModel):
    """Cleaned content output from Erebus."""

    id: UUID = Field(default_factory=uuid4, description="Unique cleaned content ID")
    draft_id: UUID = Field(..., description="Associated draft ID")

    # Content
    title: str = Field(..., min_length=1, max_length=500, description="Title")
    original_content: str = Field(..., description="Original draft content")
    cleaned_content: str = Field(..., description="Cleaned content")

    # Metrics
    metrics: CleaningMetrics = Field(..., description="Cleaning effectiveness metrics")

    # Detailed change tracking
    diff_summary: list[DiffEntry] = Field(
        default_factory=list, description="Detailed list of changes made"
    )

    # Quality gates
    passes_ai_threshold: bool = Field(..., description="True if AI-likelihood < 0.25")
    passes_voice_threshold: bool = Field(..., description="True if voice deviation < 0.35")
    passes_semantic_threshold: bool = Field(..., description="True if semantic similarity > 0.90")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    def passes_all_quality_gates(self) -> bool:
        """Check if content passes all quality gates."""
        return (
            self.passes_ai_threshold
            and self.passes_voice_threshold
            and self.passes_semantic_threshold
        )

    def get_quality_summary(self) -> dict[str, bool]:
        """Get summary of quality gate results."""
        return {
            "ai_threshold": self.passes_ai_threshold,
            "voice_threshold": self.passes_voice_threshold,
            "semantic_threshold": self.passes_semantic_threshold,
            "all_passed": self.passes_all_quality_gates(),
        }
