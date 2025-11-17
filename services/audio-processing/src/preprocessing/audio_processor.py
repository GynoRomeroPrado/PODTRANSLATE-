"""Audio preprocessing and speaker diarization."""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, List
import httpx
import ffmpeg
from pydub import AudioSegment
import librosa
import soundfile as sf
import noisereduce as nr
import numpy as np
from pyannote.audio import Pipeline

from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class AudioProcessor:
    """Audio preprocessing and speaker diarization service."""

    def __init__(self):
        """Initialize audio processor."""
        self.temp_dir = Path(settings.audio_temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Initialize diarization pipeline (lazy load)
        self._diarization_pipeline = None

    @property
    def diarization_pipeline(self):
        """Lazy load the diarization pipeline."""
        if self._diarization_pipeline is None:
            logger.info("Loading pyannote diarization pipeline")
            self._diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=settings.pyannote_auth_token
            )
        return self._diarization_pipeline

    async def download_and_preprocess(
        self,
        audio_url: str,
        job_id: str
    ) -> str:
        """
        Download audio from URL and preprocess it.

        Steps:
        1. Download audio file
        2. Convert to WAV 16kHz mono
        3. Apply noise reduction
        4. Normalize audio levels

        Args:
            audio_url: URL of the audio file
            job_id: Job identifier

        Returns:
            Path to the preprocessed audio file
        """
        try:
            # Create job-specific temp directory
            job_dir = self.temp_dir / job_id
            job_dir.mkdir(parents=True, exist_ok=True)

            # Download audio
            logger.info(f"Downloading audio from {audio_url}")
            download_path = job_dir / "original.audio"

            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                response.raise_for_status()

                with open(download_path, 'wb') as f:
                    f.write(response.content)

            # Convert to WAV 16kHz mono
            logger.info("Converting audio to WAV 16kHz mono")
            converted_path = job_dir / "converted.wav"

            ffmpeg.input(str(download_path)).output(
                str(converted_path),
                acodec='pcm_s16le',
                ac=1,  # mono
                ar='16000'  # 16kHz sample rate
            ).overwrite_output().run(quiet=True)

            # Load audio for processing
            audio_data, sample_rate = librosa.load(
                str(converted_path),
                sr=16000,
                mono=True
            )

            # Apply noise reduction
            logger.info("Applying noise reduction")
            reduced_noise = nr.reduce_noise(
                y=audio_data,
                sr=sample_rate,
                stationary=True,
                prop_decrease=0.8
            )

            # Normalize audio
            logger.info("Normalizing audio")
            normalized = librosa.util.normalize(reduced_noise)

            # Save preprocessed audio
            preprocessed_path = job_dir / "preprocessed.wav"
            sf.write(
                str(preprocessed_path),
                normalized,
                sample_rate
            )

            logger.info(f"Audio preprocessing completed: {preprocessed_path}")
            return str(preprocessed_path)

        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}", exc_info=True)
            raise

    async def diarize_speakers(
        self,
        audio_path: str
    ) -> List[Dict]:
        """
        Perform speaker diarization on the audio.

        Args:
            audio_path: Path to the audio file

        Returns:
            List of speaker segments with timestamps
        """
        try:
            logger.info("Starting speaker diarization")

            # Run diarization
            diarization = self.diarization_pipeline(audio_path)

            # Convert to list of segments
            speakers = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.append({
                    "speaker": speaker,
                    "start": turn.start,
                    "end": turn.end,
                    "duration": turn.end - turn.start
                })

            logger.info(f"Diarization completed: {len(speakers)} segments, "
                       f"{len(set(s['speaker'] for s in speakers))} unique speakers")

            return speakers

        except Exception as e:
            logger.error(f"Error during speaker diarization: {e}", exc_info=True)
            raise

    def split_by_speakers(
        self,
        audio_path: str,
        speakers: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Split audio file by speaker segments.

        Args:
            audio_path: Path to the audio file
            speakers: List of speaker segments from diarization

        Returns:
            Dictionary mapping speaker ID to list of audio segment paths
        """
        try:
            logger.info("Splitting audio by speakers")

            # Load audio
            audio = AudioSegment.from_wav(audio_path)

            # Group segments by speaker
            speaker_segments = {}
            for segment in speakers:
                speaker_id = segment['speaker']
                start_ms = int(segment['start'] * 1000)
                end_ms = int(segment['end'] * 1000)

                # Extract segment
                audio_segment = audio[start_ms:end_ms]

                if speaker_id not in speaker_segments:
                    speaker_segments[speaker_id] = []

                # Save segment
                job_dir = Path(audio_path).parent
                segment_path = job_dir / f"{speaker_id}_{len(speaker_segments[speaker_id])}.wav"

                audio_segment.export(
                    str(segment_path),
                    format="wav"
                )

                speaker_segments[speaker_id].append(str(segment_path))

            logger.info(f"Audio split into {len(speaker_segments)} speaker tracks")
            return speaker_segments

        except Exception as e:
            logger.error(f"Error splitting audio by speakers: {e}", exc_info=True)
            raise

    def cleanup_job(self, job_id: str):
        """
        Clean up temporary files for a job.

        Args:
            job_id: Job identifier
        """
        try:
            job_dir = self.temp_dir / job_id
            if job_dir.exists():
                import shutil
                shutil.rmtree(job_dir)
                logger.info(f"Cleaned up temporary files for job {job_id}")
        except Exception as e:
            logger.error(f"Error cleaning up job {job_id}: {e}")
