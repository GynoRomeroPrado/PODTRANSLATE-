"""Main FastAPI application for audio processing service."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import uuid

from .config import settings
from .preprocessing.audio_processor import AudioProcessor
from .transcription.whisper_service import WhisperService
from .translation.translation_service import TranslationService
from .tts.tts_service import TTSService
from .utils.storage import S3Storage
from .utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


# Request/Response models
class TranscriptionRequest(BaseModel):
    audio_url: Optional[HttpUrl] = None
    source_language: str = "auto"
    target_languages: List[str]
    podcast_id: str
    episode_id: str
    enable_diarization: bool = True
    enable_translation: bool = True
    enable_tts: bool = False


class TranscriptionResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    current_step: str
    transcription_url: Optional[str] = None
    translations: Optional[dict] = None
    audio_urls: Optional[dict] = None
    error: Optional[str] = None


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    logger.info("Starting audio processing service...")

    # Initialize services
    app.state.audio_processor = AudioProcessor()
    app.state.whisper_service = WhisperService()
    app.state.translation_service = TranslationService()
    app.state.tts_service = TTSService()
    app.state.storage = S3Storage()

    logger.info("Audio processing service started successfully")

    yield

    logger.info("Shutting down audio processing service...")
    # Cleanup resources
    if hasattr(app.state, 'whisper_service'):
        app.state.whisper_service.cleanup()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Audio processing service for podcast transcription and translation",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "audio-processing",
        "version": "1.0.0"
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check if models are loaded
        if not hasattr(app.state, 'whisper_service'):
            raise Exception("Whisper service not initialized")

        return {
            "status": "ready",
            "models_loaded": True
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


# Main API endpoints
@app.post("/transcribe", response_model=TranscriptionResponse)
async def create_transcription_job(
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new transcription job.

    Supports both file upload and URL-based processing.
    """
    try:
        job_id = str(uuid.uuid4())

        logger.info(f"Creating transcription job {job_id} for podcast {request.podcast_id}")

        # Add job to background tasks
        background_tasks.add_task(
            process_transcription_job,
            job_id=job_id,
            request=request
        )

        return TranscriptionResponse(
            job_id=job_id,
            status="queued",
            message="Transcription job created successfully"
        )

    except Exception as e:
        logger.error(f"Error creating transcription job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe/upload", response_model=TranscriptionResponse)
async def upload_and_transcribe(
    file: UploadFile = File(...),
    source_language: str = "auto",
    target_languages: str = "",
    podcast_id: str = "",
    episode_id: str = "",
    enable_diarization: bool = True,
    enable_translation: bool = True,
    enable_tts: bool = False,
    background_tasks: BackgroundTasks = None
):
    """
    Upload an audio file and create a transcription job.
    """
    try:
        job_id = str(uuid.uuid4())

        # Upload file to S3
        storage: S3Storage = app.state.storage
        audio_key = f"uploads/{podcast_id}/{episode_id}/{job_id}/{file.filename}"

        logger.info(f"Uploading audio file to S3: {audio_key}")
        audio_url = await storage.upload_file(
            file.file,
            settings.s3_bucket_audio,
            audio_key
        )

        # Parse target languages
        target_langs = [lang.strip() for lang in target_languages.split(",") if lang.strip()]

        # Create request object
        request = TranscriptionRequest(
            audio_url=audio_url,
            source_language=source_language,
            target_languages=target_langs,
            podcast_id=podcast_id,
            episode_id=episode_id,
            enable_diarization=enable_diarization,
            enable_translation=enable_translation,
            enable_tts=enable_tts
        )

        # Add job to background tasks
        background_tasks.add_task(
            process_transcription_job,
            job_id=job_id,
            request=request
        )

        return TranscriptionResponse(
            job_id=job_id,
            status="queued",
            message="File uploaded and transcription job created"
        )

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a transcription job."""
    try:
        # TODO: Implement job status tracking with Redis
        # For now, return a placeholder
        return JobStatus(
            job_id=job_id,
            status="processing",
            progress=50,
            current_step="transcription"
        )
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background job processor
async def process_transcription_job(job_id: str, request: TranscriptionRequest):
    """
    Background task to process transcription job.

    Steps:
    1. Download and preprocess audio
    2. Speaker diarization (if enabled)
    3. Transcribe with Whisper
    4. Translate to target languages (if enabled)
    5. Generate TTS audio (if enabled)
    6. Upload results to S3
    7. Update job status
    """
    try:
        logger.info(f"Processing job {job_id}")

        # Get services
        audio_processor: AudioProcessor = app.state.audio_processor
        whisper_service: WhisperService = app.state.whisper_service
        translation_service: TranslationService = app.state.translation_service
        tts_service: TTSService = app.state.tts_service
        storage: S3Storage = app.state.storage

        # Step 1: Download and preprocess audio
        logger.info(f"[{job_id}] Downloading and preprocessing audio")
        audio_path = await audio_processor.download_and_preprocess(
            str(request.audio_url),
            job_id
        )

        # Step 2: Speaker diarization
        speakers = None
        if request.enable_diarization:
            logger.info(f"[{job_id}] Performing speaker diarization")
            speakers = await audio_processor.diarize_speakers(audio_path)

        # Step 3: Transcribe
        logger.info(f"[{job_id}] Transcribing audio")
        transcription = await whisper_service.transcribe(
            audio_path,
            language=request.source_language if request.source_language != "auto" else None,
            speakers=speakers
        )

        # Upload original transcription
        transcript_key = f"transcripts/{request.podcast_id}/{request.episode_id}/{job_id}/original.json"
        transcript_url = await storage.upload_json(
            transcription,
            settings.s3_bucket_transcripts,
            transcript_key
        )

        # Step 4: Translate
        translations = {}
        if request.enable_translation and request.target_languages:
            logger.info(f"[{job_id}] Translating to {len(request.target_languages)} languages")

            for target_lang in request.target_languages:
                translated = await translation_service.translate(
                    transcription,
                    source_language=transcription.get('language', 'en'),
                    target_language=target_lang
                )

                # Upload translation
                trans_key = f"transcripts/{request.podcast_id}/{request.episode_id}/{job_id}/{target_lang}.json"
                trans_url = await storage.upload_json(
                    translated,
                    settings.s3_bucket_transcripts,
                    trans_key
                )

                translations[target_lang] = trans_url

        # Step 5: Generate TTS (if enabled)
        audio_urls = {}
        if request.enable_tts and translations:
            logger.info(f"[{job_id}] Generating TTS audio")

            for target_lang, translation_data in translations.items():
                # Generate audio
                tts_audio_path = await tts_service.generate_audio(
                    translation_data,
                    language=target_lang,
                    job_id=job_id
                )

                # Upload TTS audio
                tts_key = f"audio/{request.podcast_id}/{request.episode_id}/{job_id}/{target_lang}.mp3"
                tts_url = await storage.upload_file(
                    open(tts_audio_path, 'rb'),
                    settings.s3_bucket_audio,
                    tts_key
                )

                audio_urls[target_lang] = tts_url

        logger.info(f"[{job_id}] Job completed successfully")

        # TODO: Update job status in database/Redis
        # For now, just log completion

    except Exception as e:
        logger.error(f"[{job_id}] Error processing job: {e}", exc_info=True)
        # TODO: Update job status with error


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
