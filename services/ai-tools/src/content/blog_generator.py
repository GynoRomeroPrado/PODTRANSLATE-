"""Blog post generator from podcast transcripts."""

from openai import AsyncOpenAI
import os
from typing import List


class BlogGenerator:
    """Generate blog posts from podcast transcripts."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    async def generate(
        self,
        transcript: str,
        title: str,
        style: str = "informative",
        length: str = "medium"
    ) -> dict:
        """
        Generate a blog post from transcript.

        Args:
            transcript: Podcast transcript
            title: Blog post title
            style: Writing style (informative, casual, professional, newsletter)
            length: Target length (short, medium, long)

        Returns:
            Dictionary with blog post content
        """
        # Determine word count based on length
        word_counts = {
            "short": "500-800",
            "medium": "1000-1500",
            "long": "2000-3000"
        }
        target_words = word_counts.get(length, "1000-1500")

        # Adjust prompt based on style
        style_instructions = {
            "informative": "Write in a clear, educational tone. Use subheadings and bullet points.",
            "casual": "Write in a conversational, friendly tone. Use personal pronouns and casual language.",
            "professional": "Write in a formal, authoritative tone. Use industry terminology appropriately.",
            "newsletter": "Write in an engaging newsletter style with a strong hook and clear call-to-action."
        }

        style_instruction = style_instructions.get(style, style_instructions["informative"])

        prompt = f"""You are an expert content writer specializing in podcast content repurposing.

Convert the following podcast transcript into a well-structured blog post.

Title: {title}

Style: {style_instruction}
Target length: {target_words} words

Requirements:
1. Create an engaging introduction that hooks the reader
2. Structure the content with clear headings (H2, H3)
3. Include key takeaways and insights from the discussion
4. Add relevant examples and quotes from the transcript
5. Conclude with a summary and call-to-action
6. Optimize for SEO with natural keyword integration
7. Make it scannable with bullet points and short paragraphs

Transcript:
{transcript[:8000]}  # Limit to avoid token limits

Please generate the blog post in markdown format."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert content writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )

        content = response.choices[0].message.content

        # Extract metadata
        word_count = len(content.split())
        reading_time = round(word_count / 200)  # Average reading speed

        return {
            "title": title,
            "content": content,
            "html": self._markdown_to_html(content),
            "metadata": {
                "word_count": word_count,
                "reading_time_minutes": reading_time,
                "style": style,
                "generated_at": self._get_timestamp()
            }
        }

    async def generate_titles(self, transcript: str, count: int = 10) -> List[str]:
        """
        Generate multiple title suggestions.

        Args:
            transcript: Podcast transcript
            count: Number of titles to generate

        Returns:
            List of title suggestions
        """
        prompt = f"""Based on this podcast transcript, generate {count} engaging title options.

Make them:
- Attention-grabbing and clickworthy
- SEO-friendly with relevant keywords
- Varied in style (questions, lists, how-to, etc.)
- Clear about the value proposition

Transcript excerpt:
{transcript[:2000]}

Return only the titles, one per line, without numbering."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert headline writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,  # Higher temperature for creativity
            max_tokens=500
        )

        titles = response.choices[0].message.content.strip().split('\n')
        return [title.strip() for title in titles if title.strip()]

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML (basic implementation)."""
        # In production, use a proper markdown library
        import re

        html = markdown_text

        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'

        return html

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
