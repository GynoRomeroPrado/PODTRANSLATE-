"""Whisper transcription service."""

import whisper
import torch
from typing import Optional, List, Dict
from pathlib import Path

from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class WhisperService:
    """Whisper-based transcription service."""

    def __init__(self):
        """Initialize Whisper model."""
        self.device = settings.whisper_device
        self.model_name = settings.whisper_model
        self.model = None

        # Load model on initialization
        self._load_model()

    def _load_model(self):
        """Load the Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_name} on {self.device}")

            # Set device
            if self.device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                self.device = "cpu"

            # Load model
            self.model = whisper.load_model(
                self.model_name,
                device=self.device
            )

            logger.info("Whisper model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}", exc_info=True)
            raise

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        speakers: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Transcribe audio file using Whisper.

        Args:
            audio_path: Path to the audio file
            language: Source language code (None for auto-detection)
            speakers: Optional speaker diarization data

        Returns:
            Transcription result with timestamps and metadata
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")

            # Transcription options
            options = {
                "task": "transcribe",
                "word_timestamps": True,
                "verbose": False
            }

            if language:
                options["language"] = language

            # Run transcription
            result = self.model.transcribe(
                audio_path,
                **options
            )

            # Post-process results
            transcription = {
                "text": result["text"],
                "language": result["language"],
                "segments": []
            }

            # Add segment-level data
            for segment in result["segments"]:
                segment_data = {
                    "id": segment["id"],
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "words": []
                }

                # Add word-level timestamps
                if "words" in segment:
                    for word in segment["words"]:
                        segment_data["words"].append({
                            "word": word["word"].strip(),
                            "start": word["start"],
                            "end": word["end"],
                            "probability": word.get("probability", 1.0)
                        })

                # Match with speaker diarization
                if speakers:
                    segment_data["speaker"] = self._match_speaker(
                        segment["start"],
                        segment["end"],
                        speakers
                    )

                transcription["segments"].append(segment_data)

            logger.info(f"Transcription completed: {len(transcription['segments'])} segments")

            return transcription

        except Exception as e:
            logger.error(f"Error during transcription: {e}", exc_info=True)
            raise

    def _match_speaker(
        self,
        start: float,
        end: float,
        speakers: List[Dict]
    ) -> str:
        """
        Match a transcript segment to a speaker.

        Uses the speaker that has the most overlap with the segment.

        Args:
            start: Segment start time
            end: Segment end time
            speakers: List of speaker segments

        Returns:
            Speaker ID
        """
        max_overlap = 0
        matched_speaker = "SPEAKER_UNKNOWN"

        for speaker_segment in speakers:
            # Calculate overlap
            overlap_start = max(start, speaker_segment["start"])
            overlap_end = min(end, speaker_segment["end"])
            overlap = max(0, overlap_end - overlap_start)

            if overlap > max_overlap:
                max_overlap = overlap
                matched_speaker = speaker_segment["speaker"]

        return matched_speaker

    async def detect_language(self, audio_path: str) -> str:
        """
        Detect the language of an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Detected language code
        """
        try:
            # Load audio
            audio = whisper.load_audio(audio_path)

            # Detect language
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)

            logger.info(f"Detected language: {detected_language} "
                       f"(confidence: {probs[detected_language]:.2f})")

            return detected_language

        except Exception as e:
            logger.error(f"Error detecting language: {e}", exc_info=True)
            raise

    def cleanup(self):
        """Clean up resources."""
        if self.model:
            del self.model
            if self.device == "cuda":
                torch.cuda.empty_cache()
            logger.info("Whisper model cleaned up")
