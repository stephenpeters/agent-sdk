"""Shared pytest fixtures for agent-sdk tests."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from agent_sdk.models import (
    EventEnvelope,
    EventType,
    IdeaModel,
    IdeaScore,
    SourceType,
    OutlineModel,
    DraftModel,
    VoicePrint,
    CleanedContentModel,
    CleaningMetrics,
    PublishModel,
    Platform,
    EngagementMetrics,
)


@pytest.fixture
def sample_idea_id():
    """Sample idea UUID."""
    return uuid4()


@pytest.fixture
def sample_idea(sample_idea_id):
    """Sample idea model for testing."""
    return IdeaModel(
        id=sample_idea_id,
        title="The Future of AI in Healthcare",
        summary="An exploration of how AI is transforming medical diagnosis.",
        content="Full article content here...",
        source_type=SourceType.URL,
        source_url="https://example.com/ai-healthcare",
        score=IdeaScore(
            novelty=0.8,
            topicality=0.7,
            relevance=0.9,
            overall=0.8,
        ),
        topics=["AI", "Healthcare"],
        keywords=["artificial intelligence", "medical"],
    )


@pytest.fixture
def sample_outline(sample_idea_id):
    """Sample outline model for testing."""
    return OutlineModel(
        idea_id=sample_idea_id,
        title="AI Transforming Healthcare",
        define="AI in healthcare refers to...",
        contrast="Unlike traditional methods...",
        synthesize="The synthesis of AI and medical expertise...",
        project="Looking forward, we can expect...",
        key_points=["Point 1", "Point 2"],
    )


@pytest.fixture
def sample_voiceprint():
    """Sample voice print for testing."""
    return VoicePrint(
        avg_sentence_length=18.5,
        sentence_length_variance=5.2,
        paragraph_length=4.3,
        comma_frequency=12.5,
        em_dash_frequency=1.2,
        semicolon_frequency=0.5,
        lexical_diversity=0.75,
        avg_word_length=4.8,
        common_phrases=["in other words", "for example"],
        uses_questions=True,
        uses_lists=True,
        uses_examples=True,
        formality_level=0.6,
        technical_level=0.7,
    )


@pytest.fixture
def sample_draft(sample_idea_id, sample_voiceprint):
    """Sample draft model for testing."""
    return DraftModel(
        id=uuid4(),
        outline_id=uuid4(),
        idea_id=sample_idea_id,
        title="AI Transforming Healthcare",
        content="# AI Transforming Healthcare\n\nFull draft content here...",
        voice_score=0.85,
        voice_deviation=0.15,
        applied_voiceprint=sample_voiceprint,
        word_count=850,
        estimated_read_time=4,
    )


@pytest.fixture
def sample_cleaning_metrics():
    """Sample cleaning metrics for testing."""
    return CleaningMetrics(
        ai_likelihood_before=0.75,
        ai_likelihood_after=0.22,
        ai_likelihood_reduction=0.53,
        voice_deviation_before=0.40,
        voice_deviation_after=0.28,
        edit_distance=145,
        edit_percentage=17.5,
        sentences_modified=12,
        semantic_similarity=0.94,
        iterations=3,
        processing_time_ms=1250,
    )


@pytest.fixture
def sample_cleaned_content(sample_draft, sample_cleaning_metrics):
    """Sample cleaned content model for testing."""
    return CleanedContentModel(
        draft_id=sample_draft.id,
        title=sample_draft.title,
        original_content=sample_draft.content,
        cleaned_content="# AI Transforming Healthcare\n\nCleaned draft...",
        metrics=sample_cleaning_metrics,
        passes_ai_threshold=True,
        passes_voice_threshold=True,
        passes_semantic_threshold=True,
    )


@pytest.fixture
def sample_engagement_metrics():
    """Sample engagement metrics for testing."""
    return EngagementMetrics(
        views=1500,
        likes=85,
        comments=12,
        shares=23,
        clicks=45,
        engagement_rate=0.11,
    )


@pytest.fixture
def sample_publish(sample_idea_id, sample_draft, sample_cleaned_content):
    """Sample publish model for testing."""
    return PublishModel(
        content_id=sample_cleaned_content.id,
        draft_id=sample_draft.id,
        idea_id=sample_idea_id,
        title="AI Transforming Healthcare",
        content=sample_cleaned_content.cleaned_content,
        platform=Platform.LINKEDIN,
        scheduled_time=datetime.utcnow() + timedelta(hours=2),
    )


@pytest.fixture
def sample_event_envelope():
    """Sample event envelope for testing."""
    return EventEnvelope(
        type=EventType.IDEA_CREATED,
        actor="agent-aletheia",
        data_ref="s3://mnemosyne-bucket/ideas/abc123",
        meta={"source": "rss", "score": 0.85},
    )
