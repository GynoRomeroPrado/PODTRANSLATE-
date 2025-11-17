"""Initial migration - Create all tables.

Revision ID: 001
Create Date: 2024-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables."""

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('subscription_tier', sa.String(), default='free'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('key_hash', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_used_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Podcasts table
    op.create_table(
        'podcasts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('author', sa.String()),
        sa.Column('language', sa.String(), default='en'),
        sa.Column('category', sa.String()),
        sa.Column('cover_image_url', sa.String()),
        sa.Column('website_url', sa.String()),
        sa.Column('rss_feed_url', sa.String()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('settings', postgresql.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('idx_podcast_user', 'podcasts', ['user_id'])

    # Episodes table
    op.create_table(
        'episodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('podcast_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('audio_url', sa.String(), nullable=False),
        sa.Column('duration_seconds', sa.Integer()),
        sa.Column('published_at', sa.DateTime()),
        sa.Column('season_number', sa.Integer()),
        sa.Column('episode_number', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['podcast_id'], ['podcasts.id'])
    )
    op.create_index('idx_episode_podcast', 'episodes', ['podcast_id'])

    # Transcription Jobs table
    op.create_table(
        'transcription_jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('episode_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), default='queued'),
        sa.Column('progress', sa.Integer(), default=0),
        sa.Column('current_step', sa.String()),
        sa.Column('source_language', sa.String()),
        sa.Column('target_languages', postgresql.JSON(), default=[]),
        sa.Column('enable_diarization', sa.Boolean(), default=True),
        sa.Column('enable_translation', sa.Boolean(), default=True),
        sa.Column('enable_tts', sa.Boolean(), default=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['episode_id'], ['episodes.id'])
    )
    op.create_index('idx_job_episode', 'transcription_jobs', ['episode_id'])
    op.create_index('idx_job_status', 'transcription_jobs', ['status'])

    # Transcriptions table
    op.create_table(
        'transcriptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('is_original', sa.Boolean(), default=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('segments', postgresql.JSON(), nullable=False),
        sa.Column('word_count', sa.Integer()),
        sa.Column('storage_url', sa.String()),
        sa.Column('tts_audio_url', sa.String()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['transcription_jobs.id'])
    )
    op.create_index('idx_transcription_job', 'transcriptions', ['job_id'])
    op.create_index('idx_transcription_language', 'transcriptions', ['language'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('transcriptions')
    op.drop_table('transcription_jobs')
    op.drop_table('episodes')
    op.drop_table('podcasts')
    op.drop_table('api_keys')
    op.drop_table('users')
