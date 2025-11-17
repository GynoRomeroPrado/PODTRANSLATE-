"""RabbitMQ worker for processing transcription jobs."""

import pika
import json
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.preprocessing.audio_processor import AudioProcessor
from src.transcription.whisper_service import WhisperService
from src.translation.translation_service import TranslationService
from src.tts.tts_service import TTSService
from src.utils.storage import S3Storage
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptionWorker:
    """Worker for processing transcription jobs from RabbitMQ."""

    def __init__(self):
        """Initialize worker with services."""
        self.audio_processor = AudioProcessor()
        self.whisper_service = WhisperService()
        self.translation_service = TranslationService()
        self.tts_service = TTSService()
        self.storage = S3Storage()

        # Connect to RabbitMQ
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        """Connect to RabbitMQ."""
        try:
            parameters = pika.URLParameters(settings.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare queue
            self.channel.queue_declare(
                queue='transcription_jobs',
                durable=True
            )

            # Set QoS
            self.channel.basic_qos(prefetch_count=1)

            logger.info("Connected to RabbitMQ")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def process_job(self, job_data: dict):
        """
        Process a transcription job.

        Args:
            job_data: Job data from queue
        """
        job_id = job_data.get('job_id')
        audio_url = job_data.get('audio_url')
        source_language = job_data.get('source_language', 'auto')
        target_languages = job_data.get('target_languages', [])
        enable_diarization = job_data.get('enable_diarization', True)
        enable_translation = job_data.get('enable_translation', True)
        enable_tts = job_data.get('enable_tts', False)

        logger.info(f"Processing job {job_id}")

        try:
            # Step 1: Download and preprocess
            logger.info(f"[{job_id}] Preprocessing audio")
            audio_path = self.audio_processor.download_and_preprocess(
                audio_url,
                job_id
            )

            # Step 2: Diarization
            speakers = None
            if enable_diarization:
                logger.info(f"[{job_id}] Diarizing speakers")
                speakers = self.audio_processor.diarize_speakers(audio_path)

            # Step 3: Transcription
            logger.info(f"[{job_id}] Transcribing")
            transcription = self.whisper_service.transcribe(
                audio_path,
                language=source_language if source_language != 'auto' else None,
                speakers=speakers
            )

            # Upload original transcription
            transcript_key = f"transcripts/{job_id}/original.json"
            await self.storage.upload_json(
                transcription,
                settings.s3_bucket_transcripts,
                transcript_key
            )

            # Step 4: Translation
            if enable_translation and target_languages:
                logger.info(f"[{job_id}] Translating to {len(target_languages)} languages")

                for target_lang in target_languages:
                    translated = await self.translation_service.translate(
                        transcription,
                        source_language=transcription.get('language', 'en'),
                        target_language=target_lang
                    )

                    # Upload translation
                    trans_key = f"transcripts/{job_id}/{target_lang}.json"
                    await self.storage.upload_json(
                        translated,
                        settings.s3_bucket_transcripts,
                        trans_key
                    )

                    # Step 5: TTS if enabled
                    if enable_tts:
                        logger.info(f"[{job_id}] Generating TTS for {target_lang}")
                        tts_audio = await self.tts_service.generate_audio(
                            translated,
                            language=target_lang,
                            job_id=job_id
                        )

                        # Upload TTS audio
                        tts_key = f"audio/{job_id}/{target_lang}.mp3"
                        with open(tts_audio, 'rb') as f:
                            await self.storage.upload_file(
                                f,
                                settings.s3_bucket_audio,
                                tts_key
                            )

            logger.info(f"[{job_id}] Job completed successfully")

            # Cleanup temp files
            self.audio_processor.cleanup_job(job_id)

            return {
                "status": "completed",
                "job_id": job_id
            }

        except Exception as e:
            logger.error(f"[{job_id}] Job failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "job_id": job_id,
                "error": str(e)
            }

    def callback(self, ch, method, properties, body):
        """
        Callback for processing messages from queue.

        Args:
            ch: Channel
            method: Method
            properties: Properties
            body: Message body
        """
        try:
            # Parse job data
            job_data = json.loads(body)

            logger.info(f"Received job: {job_data.get('job_id')}")

            # Process job
            result = self.process_job(job_data)

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info(f"Job processed: {result}")

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # Reject and requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Start consuming messages from queue."""
        logger.info("Starting transcription worker...")

        self.channel.basic_consume(
            queue='transcription_jobs',
            on_message_callback=self.callback
        )

        logger.info("Worker is waiting for messages. To exit press CTRL+C")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"Worker error: {e}")
            self.channel.stop_consuming()
        finally:
            if self.connection:
                self.connection.close()


if __name__ == "__main__":
    worker = TranscriptionWorker()
    worker.start()
