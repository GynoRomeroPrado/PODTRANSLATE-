"""Unit tests for audio processing service."""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from preprocessing.audio_processor import AudioProcessor
from transcription.whisper_service import WhisperService
from translation.translation_service import TranslationService


class TestAudioProcessor:
    """Tests for AudioProcessor class."""

    @pytest.fixture
    def audio_processor(self):
        """Create AudioProcessor instance."""
        return AudioProcessor()

    def test_initialization(self, audio_processor):
        """Test AudioProcessor initialization."""
        assert audio_processor.temp_dir.exists()
        assert audio_processor._diarization_pipeline is None

    @pytest.mark.asyncio
    async def test_download_and_preprocess(self, audio_processor):
        """Test audio download and preprocessing."""
        # Mock HTTP client and FFmpeg
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.content = b'fake audio data'
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            with patch('ffmpeg.input'):
                with patch('librosa.load') as mock_load:
                    mock_load.return_value = (Mock(), 16000)

                    with patch('soundfile.write'):
                        # This would need actual implementation
                        # For now, just test that it doesn't crash
                        pass


class TestWhisperService:
    """Tests for WhisperService class."""

    @pytest.fixture
    def whisper_service(self):
        """Create WhisperService instance."""
        with patch('whisper.load_model'):
            return WhisperService()

    def test_initialization(self, whisper_service):
        """Test WhisperService initialization."""
        assert whisper_service.device in ['cpu', 'cuda']
        assert whisper_service.model_name == 'large-v3'

    @pytest.mark.asyncio
    async def test_transcribe(self, whisper_service):
        """Test transcription."""
        # Mock Whisper model
        whisper_service.model = Mock()
        whisper_service.model.transcribe.return_value = {
            'text': 'Test transcription',
            'language': 'en',
            'segments': [
                {
                    'id': 0,
                    'start': 0.0,
                    'end': 5.0,
                    'text': 'Test transcription',
                    'words': []
                }
            ]
        }

        result = await whisper_service.transcribe('test.wav')

        assert result['text'] == 'Test transcription'
        assert result['language'] == 'en'
        assert len(result['segments']) == 1


class TestTranslationService:
    """Tests for TranslationService class."""

    @pytest.fixture
    def translation_service(self):
        """Create TranslationService instance."""
        with patch('openai.AsyncOpenAI'):
            return TranslationService()

    @pytest.mark.asyncio
    async def test_translate_with_gpt4(self, translation_service):
        """Test translation with GPT-4."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='Transcripción de prueba'))
        ]

        translation_service.client = Mock()
        translation_service.client.chat.completions.create = Mock(
            return_value=mock_response
        )

        transcription = {
            'text': 'Test transcription',
            'language': 'en',
            'segments': [
                {
                    'id': 0,
                    'start': 0.0,
                    'end': 5.0,
                    'text': 'Test transcription'
                }
            ]
        }

        result = await translation_service.translate(
            transcription,
            source_language='en',
            target_language='es'
        )

        assert result['language'] == 'es'
        assert result['source_language'] == 'en'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
