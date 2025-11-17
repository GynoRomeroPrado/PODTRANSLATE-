"""Social media content generator."""

from openai import AsyncOpenAI
import os
from typing import List, Dict


class SocialMediaGenerator:
    """Generate social media posts from podcast content."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

        # Platform-specific configurations
        self.platform_configs = {
            "twitter": {
                "max_length": 280,
                "style": "concise and punchy",
                "hashtags": 2
            },
            "linkedin": {
                "max_length": 3000,
                "style": "professional and insightful",
                "hashtags": 3
            },
            "facebook": {
                "max_length": 500,
                "style": "engaging and conversational",
                "hashtags": 0
            },
            "instagram": {
                "max_length": 2200,
                "style": "visual and inspirational",
                "hashtags": 10
            }
        }

    async def generate(
        self,
        transcript: str,
        platforms: List[str],
        count: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        Generate social media posts for multiple platforms.

        Args:
            transcript: Podcast transcript
            platforms: List of platform names
            count: Number of posts per platform

        Returns:
            Dictionary mapping platform to list of posts
        """
        results = {}

        for platform in platforms:
            if platform not in self.platform_configs:
                continue

            posts = await self._generate_for_platform(
                transcript,
                platform,
                count
            )
            results[platform] = posts

        return results

    async def _generate_for_platform(
        self,
        transcript: str,
        platform: str,
        count: int
    ) -> List[Dict]:
        """Generate posts for a specific platform."""
        config = self.platform_configs[platform]

        prompt = f"""You are a social media expert creating content for {platform.upper()}.

Based on this podcast transcript, create {count} engaging posts.

Platform: {platform}
Style: {config['style']}
Max length: {config['max_length']} characters
Hashtags: Include {config['hashtags']} relevant hashtags

Requirements:
- Hook the reader in the first line
- Include key insights or quotes
- Add appropriate emojis (for Instagram/Facebook)
- Make it shareable and engaging
- Each post should highlight a different aspect

Transcript excerpt:
{transcript[:3000]}

Return each post on a new line, separated by "---"."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert {platform} content creator."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )

        content = response.choices[0].message.content
        posts_text = content.split('---')

        posts = []
        for i, post_text in enumerate(posts_text):
            post_text = post_text.strip()
            if not post_text:
                continue

            # Extract hashtags
            hashtags = []
            import re
            hashtag_matches = re.findall(r'#\w+', post_text)
            hashtags = hashtag_matches[:config['hashtags']]

            posts.append({
                "platform": platform,
                "content": post_text,
                "hashtags": hashtags,
                "character_count": len(post_text),
                "post_number": i + 1
            })

        return posts[:count]

    async def generate_thread(
        self,
        transcript: str,
        platform: str = "twitter",
        thread_length: int = 5
    ) -> List[str]:
        """
        Generate a Twitter/X thread.

        Args:
            transcript: Podcast transcript
            platform: Platform (currently only twitter)
            thread_length: Number of tweets in thread

        Returns:
            List of tweets forming a thread
        """
        prompt = f"""Create a Twitter thread with {thread_length} tweets from this podcast transcript.

Requirements:
- First tweet: Hook with key insight or question
- Middle tweets: Key points, one per tweet
- Last tweet: Conclusion with call-to-action
- Each tweet: Max 280 characters
- Number each tweet (1/{thread_length}, 2/{thread_length}, etc.)
- Make it valuable and shareable

Transcript:
{transcript[:3000]}

Return each tweet on a new line."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at creating viral Twitter threads."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        tweets = response.choices[0].message.content.strip().split('\n')
        return [tweet.strip() for tweet in tweets if tweet.strip()][:thread_length]
