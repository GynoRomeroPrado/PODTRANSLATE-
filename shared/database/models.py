"""Database models for PodTranslate."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class JobStatus(enum.Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DistributionStatus(enum.Enum):
    """Distribution status enumeration."""
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


# User and Organization Models
class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    subscription_tier = Column(String, default="free")  # free, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    podcasts = relationship("Podcast", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class APIKey(Base):
    """API key model."""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")


# Podcast Models
class Podcast(Base):
    """Podcast model."""
    __tablename__ = "podcasts"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    author = Column(String)
    language = Column(String, default="en")
    category = Column(String)
    cover_image_url = Column(String)
    website_url = Column(String)
    rss_feed_url = Column(String)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="podcasts")
    episodes = relationship("Episode", back_populates="podcast")
    glossaries = relationship("Glossary", back_populates="podcast")

    __table_args__ = (
        Index('idx_podcast_user', 'user_id'),
    )


class Episode(Base):
    """Podcast episode model."""
    __tablename__ = "episodes"

    id = Column(String, primary_key=True)
    podcast_id = Column(String, ForeignKey("podcasts.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    audio_url = Column(String, nullable=False)
    duration_seconds = Column(Integer)
    published_at = Column(DateTime)
    season_number = Column(Integer)
    episode_number = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    podcast = relationship("Podcast", back_populates="episodes")
    transcription_jobs = relationship("TranscriptionJob", back_populates="episode")

    __table_args__ = (
        Index('idx_episode_podcast', 'podcast_id'),
    )


# Transcription Models
class TranscriptionJob(Base):
    """Transcription job model."""
    __tablename__ = "transcription_jobs"

    id = Column(String, primary_key=True)
    episode_id = Column(String, ForeignKey("episodes.id"), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.QUEUED)
    progress = Column(Integer, default=0)
    current_step = Column(String)
    source_language = Column(String)
    target_languages = Column(JSON, default=[])
    enable_diarization = Column(Boolean, default=True)
    enable_translation = Column(Boolean, default=True)
    enable_tts = Column(Boolean, default=False)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    episode = relationship("Episode", back_populates="transcription_jobs")
    transcriptions = relationship("Transcription", back_populates="job")

    __table_args__ = (
        Index('idx_job_episode', 'episode_id'),
        Index('idx_job_status', 'status'),
    )


class Transcription(Base):
    """Transcription model."""
    __tablename__ = "transcriptions"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("transcription_jobs.id"), nullable=False)
    language = Column(String, nullable=False)
    is_original = Column(Boolean, default=False)
    text = Column(Text, nullable=False)
    segments = Column(JSON, nullable=False)
    word_count = Column(Integer)
    storage_url = Column(String)
    tts_audio_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("TranscriptionJob", back_populates="transcriptions")

    __table_args__ = (
        Index('idx_transcription_job', 'job_id'),
        Index('idx_transcription_language', 'language'),
    )


# Translation Settings
class Glossary(Base):
    """Custom glossary for podcast-specific terminology."""
    __tablename__ = "glossaries"

    id = Column(String, primary_key=True)
    podcast_id = Column(String, ForeignKey("podcasts.id"), nullable=False)
    term = Column(String, nullable=False)
    translation = Column(JSON, nullable=False)  # {lang_code: translation}
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    podcast = relationship("Podcast", back_populates="glossaries")

    __table_args__ = (
        Index('idx_glossary_podcast', 'podcast_id'),
    )


# Distribution Models
class Distribution(Base):
    """Distribution to platforms."""
    __tablename__ = "distributions"

    id = Column(String, primary_key=True)
    episode_id = Column(String, ForeignKey("episodes.id"), nullable=False)
    platform = Column(String, nullable=False)  # spotify, apple, google, youtube
    language = Column(String, nullable=False)
    status = Column(SQLEnum(DistributionStatus), default=DistributionStatus.PENDING)
    platform_id = Column(String)  # ID on the platform
    platform_url = Column(String)
    error_message = Column(Text)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_distribution_episode', 'episode_id'),
        Index('idx_distribution_platform', 'platform'),
    )


# Analytics Models (basic - ClickHouse will have more detailed analytics)
class Analytics(Base):
    """Basic analytics summary."""
    __tablename__ = "analytics"

    id = Column(String, primary_key=True)
    podcast_id = Column(String, ForeignKey("podcasts.id"), nullable=False)
    episode_id = Column(String, ForeignKey("episodes.id"))
    language = Column(String)
    metric_type = Column(String, nullable=False)  # downloads, completions, etc.
    metric_value = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_analytics_podcast', 'podcast_id'),
        Index('idx_analytics_date', 'date'),
    )


# Monetization Models
class Sponsor(Base):
    """Sponsor/advertiser model."""
    __tablename__ = "sponsors"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    logo_url = Column(String)
    website_url = Column(String)
    contact_email = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaigns = relationship("AdCampaign", back_populates="sponsor")


class AdCampaign(Base):
    """Ad campaign model."""
    __tablename__ = "ad_campaigns"

    id = Column(String, primary_key=True)
    sponsor_id = Column(String, ForeignKey("sponsors.id"), nullable=False)
    name = Column(String, nullable=False)
    ad_type = Column(String, nullable=False)  # pre_roll, mid_roll, post_roll
    target_languages = Column(JSON, default=[])
    target_categories = Column(JSON, default=[])
    cpm = Column(Float)  # Cost per mille (thousand impressions)
    budget = Column(Float)
    spent = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sponsor = relationship("Sponsor", back_populates="campaigns")


class Subscription(Base):
    """User subscription model."""
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    tier = Column(String, nullable=False)  # pro, enterprise
    status = Column(String, nullable=False)  # active, cancelled, expired
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_subscription_user', 'user_id'),
    )
