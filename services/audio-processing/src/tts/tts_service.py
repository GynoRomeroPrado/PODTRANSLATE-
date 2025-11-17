"""Text-to-speech service for generating translated audio."""

import asyncio
from pathlib import Path
from typing import Dict, Optional
import edge_tts
from gtts import gTTS
from pydub import AudioSegment
import tempfile

from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class TTSService:
    """Text-to-speech service for generating translated podcast audio."""

    def __init__(self):
        """Initialize TTS service."""
        # Voice mapping for different languages (Edge TTS voices)
        self.voice_map = {
            'en': 'en-US-AriaNeural',
            'es': 'es-ES-ElviraNeural',
            'fr': 'fr-FR-DeniseNeural',
            'de': 'de-DE-KatjaNeural',
            'it': 'it-IT-ElsaNeural',
            'pt': 'pt-BR-FranciscaNeural',
            'ru': 'ru-RU-SvetlanaNeural',
            'ja': 'ja-JP-NanamiNeural',
            'ko': 'ko-KR-SunHiNeural',
            'zh': 'zh-CN-XiaoxiaoNeural',
            'ar': 'ar-SA-ZariyahNeural',
            'hi': 'hi-IN-SwaraNeural',
            'nl': 'nl-NL-ColetteNeural',
            'pl': 'pl-PL-ZofiaNeural',
            'tr': 'tr-TR-EmelNeural',
            'vi': 'vi-VN-HoaiMyNeural',
            'th': 'th-TH-PremwadeeNeural',
            'sv': 'sv-SE-SofieNeural',
            'da': 'da-DK-ChristelNeural',
            'no': 'nb-NO-PernilleNeural',
            'fi': 'fi-FI-NooraNeural'
        }

    async def generate_audio(
        self,
        transcription: Dict,
        language: str,
        job_id: str,
        voice: Optional[str] = None
    ) -> str:
        """
        Generate TTS audio from translated transcription.

        Args:
            transcription: Translated transcription data
            language: Target language code
            job_id: Job identifier
            voice: Optional specific voice to use

        Returns:
            Path to generated audio file
        """
        try:
            logger.info(f"Generating TTS audio for language: {language}")

            # Select voice
            selected_voice = voice or self.voice_map.get(language, 'en-US-AriaNeural')

            # Create output directory
            output_dir = Path(settings.audio_temp_dir) / job_id / "tts"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate audio for each segment
            segment_files = []
            for i, segment in enumerate(transcription["segments"]):
                segment_file = await self._generate_segment(
                    text=segment["text"],
                    voice=selected_voice,
                    output_path=output_dir / f"segment_{i:04d}.mp3",
                    duration=segment["end"] - segment["start"]
                )
                segment_files.append(segment_file)

            # Combine segments
            output_file = output_dir / f"{language}_full.mp3"
            await self._combine_segments(segment_files, output_file)

            logger.info(f"TTS audio generated: {output_file}")

            return str(output_file)

        except Exception as e:
            logger.error(f"Error generating TTS audio: {e}", exc_info=True)
            raise

    async def _generate_segment(
        self,
        text: str,
        voice: str,
        output_path: Path,
        duration: Optional[float] = None
    ) -> str:
        """
        Generate TTS for a single segment.

        Args:
            text: Text to convert to speech
            voice: Voice to use
            output_path: Output file path
            duration: Optional target duration (for speed adjustment)

        Returns:
            Path to generated segment
        """
        try:
            # Use Edge TTS for generation
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))

            # Adjust speed if duration is specified
            if duration:
                await self._adjust_speed(output_path, duration)

            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating segment: {e}")
            # Fallback to gTTS if Edge TTS fails
            return await self._generate_with_gtts(text, output_path)

    async def _generate_with_gtts(
        self,
        text: str,
        output_path: Path
    ) -> str:
        """
        Fallback TTS generation using gTTS.

        Args:
            text: Text to convert
            output_path: Output file path

        Returns:
            Path to generated file
        """
        try:
            logger.info("Using gTTS as fallback")

            # Extract language code from output path or default to 'en'
            lang = 'en'

            # Generate speech
            tts = gTTS(text=text, lang=lang)
            tts.save(str(output_path))

            return str(output_path)

        except Exception as e:
            logger.error(f"gTTS generation failed: {e}")
            raise

    async def _adjust_speed(
        self,
        audio_path: Path,
        target_duration: float
    ):
        """
        Adjust audio speed to match target duration.

        Args:
            audio_path: Path to audio file
            target_duration: Target duration in seconds
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(str(audio_path))

            # Calculate current duration
            current_duration = len(audio) / 1000.0  # Convert to seconds

            # Calculate speed factor
            speed_factor = current_duration / target_duration

            # Only adjust if difference is significant
            if abs(speed_factor - 1.0) > 0.1:
                # Adjust speed (limited to reasonable range)
                speed_factor = max(0.7, min(1.3, speed_factor))

                # Apply speed change
                adjusted = audio._spawn(
                    audio.raw_data,
                    overrides={
                        "frame_rate": int(audio.frame_rate * speed_factor)
                    }
                ).set_frame_rate(audio.frame_rate)

                # Save adjusted audio
                adjusted.export(str(audio_path), format="mp3")

                logger.debug(f"Adjusted audio speed by factor {speed_factor:.2f}")

        except Exception as e:
            logger.warning(f"Could not adjust audio speed: {e}")
            # Continue without adjustment

    async def _combine_segments(
        self,
        segment_files: list,
        output_file: Path
    ):
        """
        Combine audio segments into a single file.

        Args:
            segment_files: List of segment file paths
            output_file: Output file path
        """
        try:
            logger.info(f"Combining {len(segment_files)} segments")

            # Load first segment
            combined = AudioSegment.from_file(segment_files[0])

            # Append remaining segments
            for segment_file in segment_files[1:]:
                segment = AudioSegment.from_file(segment_file)
                combined += segment

            # Export combined audio
            combined.export(
                str(output_file),
                format="mp3",
                bitrate="128k",
                parameters=["-q:a", "2"]  # High quality
            )

            logger.info(f"Combined audio saved: {output_file}")

        except Exception as e:
            logger.error(f"Error combining segments: {e}", exc_info=True)
            raise

    async def generate_preview(
        self,
        text: str,
        language: str,
        duration_seconds: int = 30
    ) -> str:
        """
        Generate a preview audio clip.

        Args:
            text: Text to convert
            language: Language code
            duration_seconds: Maximum duration

        Returns:
            Path to preview audio file
        """
        try:
            # Truncate text to approximate duration
            words = text.split()
            # Rough estimate: 150 words per minute
            max_words = int((duration_seconds / 60) * 150)
            preview_text = " ".join(words[:max_words])

            # Generate preview
            voice = self.voice_map.get(language, 'en-US-AriaNeural')
            output_path = Path(tempfile.mktemp(suffix=".mp3"))

            await self._generate_segment(
                text=preview_text,
                voice=voice,
                output_path=output_path
            )

            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            raise
