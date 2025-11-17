"""SEO-optimized show notes generator."""

from openai import AsyncOpenAI
import os
import re
from typing import List, Dict


class ShowNotesGenerator:
    """Generate SEO-optimized show notes."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    async def generate(
        self,
        transcript: str,
        include_timestamps: bool = True,
        include_keywords: bool = True
    ) -> Dict:
        """
        Generate comprehensive show notes.

        Args:
            transcript: Podcast transcript with timestamps
            include_timestamps: Whether to include topic timestamps
            include_keywords: Whether to extract SEO keywords

        Returns:
            Dictionary with show notes components
        """
        # Generate summary
        summary = await self._generate_summary(transcript)

        # Extract key points
        key_points = await self._extract_key_points(transcript)

        # Extract timestamps if needed
        timestamps = []
        if include_timestamps:
            timestamps = await self._extract_timestamps(transcript)

        # Extract keywords if needed
        keywords = []
        if include_keywords:
            keywords = await self.extract_keywords(transcript)

        # Extract resources mentioned
        resources = await self._extract_resources(transcript)

        # Generate meta description
        meta_description = await self._generate_meta_description(summary)

        return {
            "summary": summary,
            "key_points": key_points,
            "timestamps": timestamps,
            "keywords": keywords,
            "resources": resources,
            "meta_description": meta_description,
            "structured_data": self._generate_structured_data(
                summary,
                key_points,
                keywords
            )
        }

    async def _generate_summary(self, transcript: str) -> str:
        """Generate episode summary."""
        prompt = f"""Write a compelling 2-3 paragraph summary of this podcast episode.

Make it:
- Engaging and informative
- SEO-friendly with natural keyword usage
- Clear about the value listeners will get
- Professional yet accessible

Transcript:
{transcript[:4000]}"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert podcast show notes writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    async def _extract_key_points(self, transcript: str) -> List[str]:
        """Extract key takeaways."""
        prompt = f"""Extract 5-7 key takeaways from this podcast episode.

Format as bullet points, each highlighting a valuable insight or action item.

Transcript:
{transcript[:4000]}

Return only the bullet points, one per line, without numbers."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at identifying key insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )

        points = response.choices[0].message.content.strip().split('\n')
        return [point.strip('- ').strip() for point in points if point.strip()]

    async def _extract_timestamps(self, transcript: str) -> List[Dict]:
        """Extract topic timestamps from transcript."""
        prompt = f"""Analyze this transcript and identify major topic changes.

For each topic, provide:
- Timestamp (in format MM:SS or HH:MM:SS)
- Topic title (short, descriptive)

Transcript:
{transcript[:5000]}

Format: "MM:SS - Topic Title" (one per line)"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing podcast content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )

        timestamps = []
        lines = response.choices[0].message.content.strip().split('\n')

        for line in lines:
            match = re.match(r'(\d+:\d+(?::\d+)?)\s*-\s*(.+)', line.strip())
            if match:
                timestamp, topic = match.groups()
                timestamps.append({
                    "timestamp": timestamp,
                    "topic": topic.strip()
                })

        return timestamps

    async def extract_keywords(self, transcript: str) -> Dict:
        """Extract SEO keywords."""
        prompt = f"""Analyze this podcast transcript and extract SEO keywords.

Identify:
1. Primary keywords (1-2): Main topics of the episode
2. Secondary keywords (3-5): Supporting topics
3. Long-tail keywords (5-10): Specific phrases people might search
4. Related topics (5): Contextually related subjects

Transcript:
{transcript[:4000]}

Format your response as:
PRIMARY: keyword1, keyword2
SECONDARY: keyword1, keyword2, keyword3
LONG_TAIL: phrase1, phrase2, phrase3
RELATED: topic1, topic2, topic3"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an SEO expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        content = response.choices[0].message.content

        # Parse response
        keywords = {
            "primary": [],
            "secondary": [],
            "long_tail": [],
            "related": []
        }

        for line in content.split('\n'):
            if line.startswith('PRIMARY:'):
                keywords['primary'] = [k.strip() for k in line.replace('PRIMARY:', '').split(',')]
            elif line.startswith('SECONDARY:'):
                keywords['secondary'] = [k.strip() for k in line.replace('SECONDARY:', '').split(',')]
            elif line.startswith('LONG_TAIL:'):
                keywords['long_tail'] = [k.strip() for k in line.replace('LONG_TAIL:', '').split(',')]
            elif line.startswith('RELATED:'):
                keywords['related'] = [k.strip() for k in line.replace('RELATED:', '').split(',')]

        return keywords

    async def _extract_resources(self, transcript: str) -> List[Dict]:
        """Extract resources mentioned (books, tools, websites, etc.)."""
        prompt = f"""Identify any resources mentioned in this transcript:
- Books
- Tools/Software
- Websites
- People/Experts
- Companies/Products

Transcript:
{transcript[:4000]}

Format: "Type: Name - Brief description" (one per line)
If no resources mentioned, return "None""""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at extracting references."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        resources = []
        content = response.choices[0].message.content.strip()

        if content.lower() != 'none':
            lines = content.split('\n')
            for line in lines:
                match = re.match(r'(\w+):\s*(.+?)\s*-\s*(.+)', line.strip())
                if match:
                    resource_type, name, description = match.groups()
                    resources.append({
                        "type": resource_type.strip(),
                        "name": name.strip(),
                        "description": description.strip()
                    })

        return resources

    async def _generate_meta_description(self, summary: str) -> str:
        """Generate SEO meta description."""
        prompt = f"""Based on this episode summary, write a compelling meta description for SEO.

Requirements:
- 150-160 characters
- Include primary keyword naturally
- Engaging and clickworthy
- Clear value proposition

Summary:
{summary}"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an SEO copywriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    def _generate_structured_data(
        self,
        summary: str,
        key_points: List[str],
        keywords: Dict
    ) -> Dict:
        """Generate schema.org structured data for SEO."""
        return {
            "@context": "https://schema.org",
            "@type": "PodcastEpisode",
            "description": summary,
            "about": key_points,
            "keywords": ", ".join(keywords.get('primary', []) + keywords.get('secondary', []))
        }
