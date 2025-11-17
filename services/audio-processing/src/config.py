"""Configuration settings for the audio processing service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "PodTranslate Audio Processing"
    debug: bool = False
    port: int = 3001

    # Database
    database_url: str

    # Message Queue
    rabbitmq_url: str
    redis_url: str

    # Storage
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    s3_bucket_audio: str
    s3_bucket_transcripts: str

    # AI Services
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    deepl_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Whisper Configuration
    whisper_model: str = "large-v3"
    whisper_device: str = "cpu"  # or "cuda"

    # Pyannote Configuration
    pyannote_auth_token: str

    # TTS Configuration
    enable_tts: bool = True
    elevenlabs_api_key: Optional[str] = None

    # Processing
    max_concurrent_jobs: int = 5
    audio_temp_dir: str = "/tmp/audio"
    models_cache_dir: str = "/tmp/models"

    # Performance
    chunk_duration_seconds: int = 30
    max_audio_duration_seconds: int = 10800  # 3 hours

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
