"""Event collector for analytics."""

import clickhouse_connect
import os
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class EventCollector:
    """Collect and store analytics events in ClickHouse."""

    def __init__(self):
        """Initialize ClickHouse connection."""
        clickhouse_url = os.getenv("CLICKHOUSE_URL", "http://localhost:8123")
        host, port = self._parse_url(clickhouse_url)

        self.client = clickhouse_connect.get_client(
            host=host,
            port=int(port),
            database=os.getenv("CLICKHOUSE_DATABASE", "podtranslate_analytics")
        )

        # Ensure tables exist
        self._create_tables()

    def _parse_url(self, url: str) -> tuple:
        """Parse ClickHouse URL."""
        url = url.replace("http://", "").replace("https://", "")
        if ":" in url:
            host, port = url.split(":")
        else:
            host, port = url, "8123"
        return host, port

    def _create_tables(self):
        """Create analytics tables if they don't exist."""
        try:
            # Events table
            self.client.command("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id String,
                    event_type String,
                    podcast_id String,
                    episode_id String,
                    language String,
                    user_id String,
                    timestamp DateTime,
                    date Date,
                    country String,
                    region String,
                    city String,
                    device_type String,
                    platform String,
                    metadata String
                ) ENGINE = MergeTree()
                PARTITION BY toYYYYMM(date)
                ORDER BY (podcast_id, date, timestamp)
            """)

            logger.info("Analytics tables created/verified")

        except Exception as e:
            logger.error(f"Error creating tables: {e}")

    async def collect(
        self,
        event_type: str,
        podcast_id: str,
        episode_id: Optional[str] = None,
        language: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Collect an analytics event.

        Args:
            event_type: Type of event (download, play, completion, etc.)
            podcast_id: Podcast identifier
            episode_id: Episode identifier
            language: Content language
            user_id: User identifier
            metadata: Additional event metadata
        """
        try:
            import uuid
            import json

            event_id = str(uuid.uuid4())
            now = datetime.utcnow()

            # Extract geo and device info from metadata
            geo = metadata.get("geo", {}) if metadata else {}
            device = metadata.get("device", {}) if metadata else {}

            data = {
                "event_id": event_id,
                "event_type": event_type,
                "podcast_id": podcast_id,
                "episode_id": episode_id or "",
                "language": language or "",
                "user_id": user_id or "",
                "timestamp": now,
                "date": now.date(),
                "country": geo.get("country", ""),
                "region": geo.get("region", ""),
                "city": geo.get("city", ""),
                "device_type": device.get("type", ""),
                "platform": device.get("platform", ""),
                "metadata": json.dumps(metadata or {})
            }

            self.client.insert("events", [data])

            logger.info(f"Event collected: {event_type} for {podcast_id}")

        except Exception as e:
            logger.error(f"Error collecting event: {e}")
            raise
