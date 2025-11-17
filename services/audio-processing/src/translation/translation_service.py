"""Translation service using GPT-4 and DeepL."""

import asyncio
from typing import Dict, List, Optional
import deepl
from openai import AsyncOpenAI

from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class TranslationService:
    """Multi-engine translation service with context preservation."""

    def __init__(self):
        """Initialize translation service."""
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Initialize DeepL if API key is provided
        self.deepl_translator = None
        if settings.deepl_api_key:
            self.deepl_translator = deepl.Translator(settings.deepl_api_key)

        # Language name mapping
        self.language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'pl': 'Polish',
            'tr': 'Turkish',
            'vi': 'Vietnamese',
            'th': 'Thai',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish'
        }

    async def translate(
        self,
        transcription: Dict,
        source_language: str,
        target_language: str,
        use_gpt4: bool = True,
        preserve_speakers: bool = True
    ) -> Dict:
        """
        Translate transcription to target language.

        Args:
            transcription: Transcription data from Whisper
            source_language: Source language code
            target_language: Target language code
            use_gpt4: Whether to use GPT-4 (better context) or DeepL (faster)
            preserve_speakers: Whether to preserve speaker labels

        Returns:
            Translated transcription with same structure
        """
        try:
            logger.info(f"Translating from {source_language} to {target_language}")

            # Choose translation engine
            if use_gpt4 or not self.deepl_translator:
                return await self._translate_with_gpt4(
                    transcription,
                    source_language,
                    target_language,
                    preserve_speakers
                )
            else:
                return await self._translate_with_deepl(
                    transcription,
                    source_language,
                    target_language
                )

        except Exception as e:
            logger.error(f"Error during translation: {e}", exc_info=True)
            raise

    async def _translate_with_gpt4(
        self,
        transcription: Dict,
        source_language: str,
        target_language: str,
        preserve_speakers: bool
    ) -> Dict:
        """
        Translate using GPT-4 for better context and naturalness.

        Translates in chunks to maintain context while staying within token limits.
        """
        logger.info("Using GPT-4 for translation")

        source_lang_name = self.language_names.get(source_language, source_language)
        target_lang_name = self.language_names.get(target_language, target_language)

        # Prepare translation
        translated = {
            "text": "",
            "language": target_language,
            "source_language": source_language,
            "segments": []
        }

        # Translate segments in batches to maintain context
        batch_size = 10
        segments = transcription["segments"]

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]

            # Prepare batch text
            batch_texts = []
            for seg in batch:
                text = seg["text"]
                if preserve_speakers and "speaker" in seg:
                    batch_texts.append(f"[{seg['speaker']}]: {text}")
                else:
                    batch_texts.append(text)

            combined_text = "\n".join(batch_texts)

            # Create translation prompt
            system_prompt = f"""You are a professional translator specializing in podcast transcriptions.
Translate the following text from {source_lang_name} to {target_lang_name}.

Guidelines:
- Maintain the natural, conversational tone of a podcast
- Preserve technical terms and proper nouns when appropriate
- Keep speaker labels intact (format: [SPEAKER_X]: text)
- Translate idioms to equivalent expressions in the target language
- Maintain paragraph and line breaks
- Focus on natural fluency over literal translation

Translate accurately while keeping the conversational style."""

            # Call GPT-4
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_text}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            translated_text = response.choices[0].message.content
            translated_lines = translated_text.strip().split("\n")

            # Map translations back to segments
            for j, seg in enumerate(batch):
                if j < len(translated_lines):
                    line = translated_lines[j]

                    # Extract speaker if present
                    speaker = None
                    if preserve_speakers and line.startswith("["):
                        parts = line.split("]: ", 1)
                        if len(parts) == 2:
                            speaker = parts[0][1:]  # Remove [
                            line = parts[1]

                    translated_segment = {
                        "id": seg["id"],
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": line.strip()
                    }

                    if speaker:
                        translated_segment["speaker"] = speaker
                    elif "speaker" in seg:
                        translated_segment["speaker"] = seg["speaker"]

                    translated["segments"].append(translated_segment)

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)

        # Combine all segments into full text
        translated["text"] = " ".join(seg["text"] for seg in translated["segments"])

        logger.info(f"Translation completed: {len(translated['segments'])} segments")

        return translated

    async def _translate_with_deepl(
        self,
        transcription: Dict,
        source_language: str,
        target_language: str
    ) -> Dict:
        """
        Translate using DeepL API for speed.

        Note: DeepL is faster but may lose some context compared to GPT-4.
        """
        logger.info("Using DeepL for translation")

        # Map language codes to DeepL format
        deepl_source = source_language.upper()
        deepl_target = target_language.upper()

        # Special handling for some languages
        if deepl_target == "EN":
            deepl_target = "EN-US"
        elif deepl_target == "PT":
            deepl_target = "PT-BR"

        # Prepare translation
        translated = {
            "text": "",
            "language": target_language,
            "source_language": source_language,
            "segments": []
        }

        # Translate segments
        for segment in transcription["segments"]:
            result = self.deepl_translator.translate_text(
                segment["text"],
                source_lang=deepl_source,
                target_lang=deepl_target
            )

            translated_segment = {
                "id": segment["id"],
                "start": segment["start"],
                "end": segment["end"],
                "text": result.text
            }

            if "speaker" in segment:
                translated_segment["speaker"] = segment["speaker"]

            translated["segments"].append(translated_segment)

        # Combine all segments
        translated["text"] = " ".join(seg["text"] for seg in translated["segments"])

        logger.info(f"DeepL translation completed: {len(translated['segments'])} segments")

        return translated

    async def translate_batch(
        self,
        transcription: Dict,
        target_languages: List[str],
        source_language: str
    ) -> Dict[str, Dict]:
        """
        Translate to multiple target languages in parallel.

        Args:
            transcription: Source transcription
            target_languages: List of target language codes
            source_language: Source language code

        Returns:
            Dictionary mapping language code to translated transcription
        """
        logger.info(f"Batch translating to {len(target_languages)} languages")

        # Create translation tasks
        tasks = []
        for target_lang in target_languages:
            task = self.translate(
                transcription,
                source_language,
                target_lang
            )
            tasks.append((target_lang, task))

        # Run translations in parallel
        results = {}
        for target_lang, task in tasks:
            try:
                results[target_lang] = await task
            except Exception as e:
                logger.error(f"Error translating to {target_lang}: {e}")
                results[target_lang] = {"error": str(e)}

        return results
