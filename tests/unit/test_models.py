"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from agent_sdk.models import (
    EventEnvelope,
    EventType,
    IdeaModel,
    IdeaScore,
    IdeaStatus,
    SourceType,
    OutlineModel,
    DraftModel,
    DraftStatus,
    CleanedContentModel,
    PublishModel,
    PublishStatus,
    Platform,
)


class TestEventEnvelope:
    """Tests for EventEnvelope model."""

    def test_create_event_envelope(self):
        """Test creating an event envelope."""
        event = EventEnvelope(
            type=EventType.IDEA_CREATED,
            actor="agent-aletheia",
            data_ref="s3://bucket/key",
        )

        assert event.type == EventType.IDEA_CREATED
        assert event.actor == "agent-aletheia"
        assert event.id is not None
        assert event.timestamp is not None

    def test_event_serialization(self, sample_event_envelope):
        """Test event can be serialized to/from JSON."""
        json_str = sample_event_envelope.model_dump_json_str()
        assert isinstance(json_str, str)

        deserialized = EventEnvelope.from_json_str(json_str)
        assert deserialized.type == sample_event_envelope.type
        assert deserialized.actor == sample_event_envelope.actor


class TestIdeaModel:
    """Tests for IdeaModel."""

    def test_create_idea(self, sample_idea):
        """Test creating an idea model."""
        assert sample_idea.title == "The Future of AI in Healthcare"
        assert sample_idea.source_type == SourceType.URL
        assert sample_idea.status == IdeaStatus.PROCESSING

    def test_idea_threshold_check(self, sample_idea):
        """Test idea threshold checking."""
        assert sample_idea.is_above_threshold(0.65)
        assert not sample_idea.is_above_threshold(0.9)

    def test_idea_approval(self, sample_idea):
        """Test idea approval workflow."""
        sample_idea.approve()
        assert sample_idea.status == IdeaStatus.APPROVED

    def test_idea_rejection(self, sample_idea):
        """Test idea rejection workflow."""
        sample_idea.reject()
        assert sample_idea.status == IdeaStatus.REJECTED


class TestOutlineModel:
    """Tests for OutlineModel."""

    def test_create_outline(self, sample_outline):
        """Test creating an outline model."""
        assert sample_outline.title == "AI Transforming Healthcare"
        assert len(sample_outline.define) > 0

    def test_get_full_outline(self, sample_outline):
        """Test full outline formatting."""
        full_text = sample_outline.get_full_outline()
        assert "# AI Transforming Healthcare" in full_text
        assert "## Define" in full_text


class TestDraftModel:
    """Tests for DraftModel."""

    def test_create_draft(self, sample_draft):
        """Test creating a draft model."""
        assert sample_draft.title == "AI Transforming Healthcare"
        assert sample_draft.word_count == 850

    def test_mark_draft_ready(self, sample_draft):
        """Test marking draft as ready."""
        sample_draft.mark_ready()
        assert sample_draft.status == DraftStatus.READY


class TestCleanedContentModel:
    """Tests for CleanedContentModel."""

    def test_all_quality_gates_pass(self, sample_cleaned_content):
        """Test all quality gates passing."""
        assert sample_cleaned_content.passes_all_quality_gates()

    def test_quality_summary(self, sample_cleaned_content):
        """Test quality summary generation."""
        summary = sample_cleaned_content.get_quality_summary()
        assert summary["all_passed"] is True


class TestPublishModel:
    """Tests for PublishModel."""

    def test_create_publish(self, sample_publish):
        """Test creating publish model."""
        assert sample_publish.platform == Platform.LINKEDIN
        assert sample_publish.status == PublishStatus.PENDING_APPROVAL

    def test_publish_approval(self, sample_publish):
        """Test publish approval workflow."""
        sample_publish.approve(notes="Looks good!")
        assert sample_publish.status == PublishStatus.APPROVED

    def test_publish_workflow(self, sample_publish):
        """Test complete publish workflow."""
        sample_publish.approve()
        assert sample_publish.status == PublishStatus.APPROVED

        sample_publish.mark_publishing()
        assert sample_publish.status == PublishStatus.PUBLISHING

        sample_publish.mark_published(
            platform_post_id="linkedin-12345",
            platform_url="https://linkedin.com/posts/12345",
        )
        assert sample_publish.status == PublishStatus.PUBLISHED
