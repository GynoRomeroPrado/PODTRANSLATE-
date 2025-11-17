#!/usr/bin/env python3
"""
PodTranslate Python SDK Example

Simple client library for interacting with PodTranslate API.
"""

import requests
from typing import List, Optional, Dict
import time


class PodTranslateClient:
    """Client for PodTranslate API."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:3000/api/v1"):
        """
        Initialize client.

        Args:
            api_key: Your API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })

    def create_transcription(
        self,
        audio_file_path: str,
        podcast_id: str,
        episode_id: str,
        source_language: str = "auto",
        target_languages: Optional[List[str]] = None,
        enable_diarization: bool = True,
        enable_translation: bool = True,
        enable_tts: bool = False
    ) -> Dict:
        """
        Upload audio file and create transcription job.

        Args:
            audio_file_path: Path to audio file
            podcast_id: Podcast ID
            episode_id: Episode ID
            source_language: Source language code (default: auto)
            target_languages: List of target languages for translation
            enable_diarization: Enable speaker diarization
            enable_translation: Enable translation
            enable_tts: Enable text-to-speech generation

        Returns:
            Job information
        """
        with open(audio_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'podcast_id': podcast_id,
                'episode_id': episode_id,
                'source_language': source_language,
                'target_languages': ','.join(target_languages or []),
                'enable_diarization': str(enable_diarization).lower(),
                'enable_translation': str(enable_translation).lower(),
                'enable_tts': str(enable_tts).lower()
            }

            # Remove API key header for multipart upload
            headers = {'X-API-Key': self.api_key}

            response = requests.post(
                f"{self.base_url}/transcriptions/upload",
                files=files,
                data=data,
                headers=headers
            )

            response.raise_for_status()
            return response.json()

    def get_job_status(self, job_id: str) -> Dict:
        """
        Get transcription job status.

        Args:
            job_id: Job ID

        Returns:
            Job status information
        """
        response = self.session.get(f"{self.base_url}/transcriptions/{job_id}")
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        job_id: str,
        timeout: int = 3600,
        poll_interval: int = 10
    ) -> Dict:
        """
        Wait for job to complete.

        Args:
            job_id: Job ID
            timeout: Maximum time to wait (seconds)
            poll_interval: Time between status checks (seconds)

        Returns:
            Final job status

        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)

            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(f"Job failed: {status.get('error')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Job did not complete within {timeout} seconds")

    def generate_blog_post(
        self,
        transcript: str,
        title: str,
        style: str = "informative",
        length: str = "medium"
    ) -> Dict:
        """
        Generate blog post from transcript.

        Args:
            transcript: Podcast transcript
            title: Blog post title
            style: Writing style (informative, casual, professional)
            length: Target length (short, medium, long)

        Returns:
            Generated blog post
        """
        response = self.session.post(
            f"{self.base_url}/ai-tools/generate/blog",
            json={
                'transcript': transcript,
                'title': title,
                'style': style,
                'length': length
            }
        )
        response.raise_for_status()
        return response.json()

    def generate_social_media(
        self,
        transcript: str,
        platforms: List[str]
    ) -> Dict:
        """
        Generate social media posts.

        Args:
            transcript: Podcast transcript
            platforms: List of platforms (twitter, linkedin, facebook, instagram)

        Returns:
            Generated social media posts
        """
        response = self.session.post(
            f"{self.base_url}/ai-tools/generate/social",
            json={
                'transcript': transcript,
                'platforms': platforms,
                'count': 5
            }
        )
        response.raise_for_status()
        return response.json()

    def get_analytics(
        self,
        podcast_id: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Get podcast analytics.

        Args:
            podcast_id: Podcast ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Analytics data
        """
        response = self.session.get(
            f"{self.base_url}/analytics/podcasts/{podcast_id}",
            params={
                'start_date': start_date,
                'end_date': end_date
            }
        )
        response.raise_for_status()
        return response.json()


# Example usage
def main():
    """Example usage of PodTranslate SDK."""

    # Initialize client
    client = PodTranslateClient(
        api_key="your-api-key-here",
        base_url="http://localhost:3000/api/v1"
    )

    # Upload and transcribe
    print("📤 Uploading audio file...")
    job = client.create_transcription(
        audio_file_path="podcast_episode.mp3",
        podcast_id="my-podcast",
        episode_id="episode-001",
        source_language="en",
        target_languages=["es", "fr", "de"],
        enable_diarization=True,
        enable_translation=True
    )

    print(f"✅ Job created: {job['job_id']}")

    # Wait for completion
    print("⏳ Waiting for transcription to complete...")
    result = client.wait_for_completion(job['job_id'])

    print(f"✅ Transcription completed!")
    print(f"   Transcription URL: {result['transcription_url']}")
    print(f"   Translations: {list(result['translations'].keys())}")

    # Generate blog post
    print("\n📝 Generating blog post...")
    blog = client.generate_blog_post(
        transcript=result['transcript']['text'],
        title="My Awesome Podcast Episode",
        style="informative"
    )

    print(f"✅ Blog post generated ({blog['metadata']['word_count']} words)")

    # Generate social media
    print("\n📱 Generating social media posts...")
    social = client.generate_social_media(
        transcript=result['transcript']['text'],
        platforms=["twitter", "linkedin"]
    )

    print(f"✅ Social media posts generated:")
    for platform, posts in social['social_media'].items():
        print(f"   {platform}: {len(posts)} posts")

    # Get analytics
    print("\n📊 Fetching analytics...")
    analytics = client.get_analytics(
        podcast_id="my-podcast",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )

    print(f"✅ Analytics retrieved:")
    print(f"   Total downloads: {analytics['metrics']['downloads']['total']}")
    print(f"   By language: {analytics['metrics']['downloads']['by_language']}")


if __name__ == "__main__":
    main()
