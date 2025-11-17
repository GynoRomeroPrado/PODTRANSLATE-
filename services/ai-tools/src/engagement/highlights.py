"""Highlight and quotable moments extractor."""

from openai import AsyncOpenAI
import os
from typing import List, Dict


class HighlightGenerator:
    """Extract highlights and quotable moments."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    async def generate(self, transcript: str) -> Dict:
        """
        Extract highlights from transcript.

        Args:
            transcript: Podcast transcript

        Returns:
            Dictionary with different types of highlights
        """
        # Extract quotable moments
        quotes = await self._extract_quotes(transcript)

        # Extract key insights
        insights = await self._extract_insights(transcript)

        # Extract surprising moments
        surprises = await self._extract_surprises(transcript)

        # Extract actionable takeaways
        actionables = await self._extract_actionables(transcript)

        return {
            "quotes": quotes,
            "insights": insights,
            "surprises": surprises,
            "actionables": actionables
        }

    async def _extract_quotes(self, transcript: str) -> List[Dict]:
        """Extract quotable, shareable moments."""
        prompt = f"""Extract 5-7 highly quotable moments from this transcript.

Look for:
- Memorable one-liners
- Powerful statements
- Wisdom or insights
- Provocative or thought-provoking statements

Each quote should:
- Stand alone without context
- Be shareable on social media
- Be impactful and memorable

Transcript:
{transcript[:5000]}

Format: Just the quote text, one per line."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at identifying quotable moments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=800
        )

        quotes = []
        lines = response.choices[0].message.content.strip().split('\n')

        for i, line in enumerate(lines):
            quote_text = line.strip().strip('"').strip("'")
            if quote_text:
                quotes.append({
                    "text": quote_text,
                    "type": "quote",
                    "shareability": "high",
                    "id": i + 1
                })

        return quotes

    async def _extract_insights(self, transcript: str) -> List[Dict]:
        """Extract key insights and learnings."""
        prompt = f"""Identify 5-7 key insights or learnings from this transcript.

Look for:
- Important revelations
- Expert advice
- Unique perspectives
- Valuable knowledge

Transcript:
{transcript[:5000]}

Format: Brief insight (1-2 sentences), one per line."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at distilling key insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )

        insights = []
        lines = response.choices[0].message.content.strip().split('\n')

        for i, line in enumerate(lines):
            if line.strip():
                insights.append({
                    "text": line.strip(),
                    "type": "insight",
                    "id": i + 1
                })

        return insights

    async def _extract_surprises(self, transcript: str) -> List[str]:
        """Extract surprising or unexpected moments."""
        prompt = f"""Identify 3-5 surprising or unexpected moments from this discussion.

Look for:
- Counterintuitive ideas
- Surprising statistics or facts
- Unexpected revelations
- Plot twists in the narrative

Transcript:
{transcript[:5000]}

Format: One surprising moment per line."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at identifying surprising content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )

        surprises = response.choices[0].message.content.strip().split('\n')
        return [s.strip() for s in surprises if s.strip()]

    async def _extract_actionables(self, transcript: str) -> List[Dict]:
        """Extract actionable takeaways."""
        prompt = f"""Extract 5 actionable takeaways listeners can implement.

Each should be:
- Specific and concrete
- Immediately actionable
- Practical and useful

Transcript:
{transcript[:5000]}

Format: Action item (starting with a verb), one per line."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at creating actionable advice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )

        actionables = []
        lines = response.choices[0].message.content.strip().split('\n')

        for i, line in enumerate(lines):
            if line.strip():
                actionables.append({
                    "action": line.strip(),
                    "priority": "medium",
                    "id": i + 1
                })

        return actionables
