"""Analytics queries for ClickHouse."""

import clickhouse_connect
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class AnalyticsQueries:
    """Execute analytics queries against ClickHouse."""

    def __init__(self):
        """Initialize ClickHouse connection."""
        clickhouse_url = os.getenv("CLICKHOUSE_URL", "http://localhost:8123")
        host, port = self._parse_url(clickhouse_url)

        self.client = clickhouse_connect.get_client(
            host=host,
            port=int(port),
            database=os.getenv("CLICKHOUSE_DATABASE", "podtranslate_analytics")
        )

    def _parse_url(self, url: str) -> tuple:
        """Parse ClickHouse URL."""
        url = url.replace("http://", "").replace("https://", "")
        if ":" in url:
            host, port = url.split(":")
        else:
            host, port = url, "8123"
        return host, port

    async def get_podcast_metrics(
        self,
        podcast_id: str,
        start_date: str,
        end_date: str,
        group_by: str = "day"
    ) -> Dict:
        """Get aggregated metrics for a podcast."""
        try:
            # Total downloads
            downloads_query = f"""
                SELECT count(*) as total
                FROM events
                WHERE podcast_id = '{podcast_id}'
                AND event_type = 'download'
                AND date BETWEEN '{start_date}' AND '{end_date}'
            """

            downloads = self.client.query(downloads_query).result_rows
            total_downloads = downloads[0][0] if downloads else 0

            # By language
            language_query = f"""
                SELECT language, count(*) as count
                FROM events
                WHERE podcast_id = '{podcast_id}'
                AND event_type = 'download'
                AND date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY language
                ORDER BY count DESC
            """

            language_results = self.client.query(language_query).result_rows
            by_language = {row[0]: row[1] for row in language_results}

            # By region
            region_query = f"""
                SELECT country, count(*) as count
                FROM events
                WHERE podcast_id = '{podcast_id}'
                AND event_type = 'download'
                AND date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY country
                ORDER BY count DESC
                LIMIT 10
            """

            region_results = self.client.query(region_query).result_rows
            by_region = {row[0]: row[1] for row in region_results}

            return {
                "downloads": {
                    "total": total_downloads,
                    "by_language": by_language,
                    "by_region": by_region
                }
            }

        except Exception as e:
            logger.error(f"Error querying podcast metrics: {e}")
            return {}

    async def get_episode_metrics(
        self,
        episode_id: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """Get metrics for a specific episode."""
        try:
            query = f"""
                SELECT
                    event_type,
                    count(*) as count
                FROM events
                WHERE episode_id = '{episode_id}'
                AND date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY event_type
            """

            results = self.client.query(query).result_rows
            metrics = {row[0]: row[1] for row in results}

            return metrics

        except Exception as e:
            logger.error(f"Error querying episode metrics: {e}")
            return {}

    async def get_language_performance(
        self,
        podcast_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """Get performance metrics by language."""
        try:
            query = f"""
                SELECT
                    language,
                    count(*) as downloads,
                    countIf(event_type = 'completion') as completions,
                    round(completions / downloads * 100, 2) as completion_rate
                FROM events
                WHERE podcast_id = '{podcast_id}'
                AND date BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY language
                ORDER BY downloads DESC
            """

            results = self.client.query(query).result_rows

            languages = []
            for row in results:
                languages.append({
                    "language": row[0],
                    "downloads": row[1],
                    "completions": row[2],
                    "completion_rate": row[3]
                })

            return languages

        except Exception as e:
            logger.error(f"Error querying language performance: {e}")
            return []

    async def get_geographic_distribution(
        self,
        podcast_id: str,
        start_date: str,
        end_date: str,
        language: Optional[str] = None
    ) -> List[Dict]:
        """Get geographic distribution of listeners."""
        try:
            lang_filter = f"AND language = '{language}'" if language else ""

            query = f"""
                SELECT
                    country,
                    count(*) as downloads
                FROM events
                WHERE podcast_id = '{podcast_id}'
                AND event_type = 'download'
                AND date BETWEEN '{start_date}' AND '{end_date}'
                {lang_filter}
                GROUP BY country
                ORDER BY downloads DESC
                LIMIT 50
            """

            results = self.client.query(query).result_rows

            geography = []
            for row in results:
                geography.append({
                    "country": row[0],
                    "downloads": row[1]
                })

            return geography

        except Exception as e:
            logger.error(f"Error querying geographic distribution: {e}")
            return []

    async def get_trending(
        self,
        period: str = "7d",
        language: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get trending podcasts."""
        try:
            # Calculate date range based on period
            days = int(period.replace("d", ""))
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)

            lang_filter = f"AND language = '{language}'" if language else ""

            query = f"""
                SELECT
                    podcast_id,
                    count(*) as downloads
                FROM events
                WHERE event_type = 'download'
                AND date BETWEEN '{start_date}' AND '{end_date}'
                {lang_filter}
                GROUP BY podcast_id
                ORDER BY downloads DESC
                LIMIT {limit}
            """

            results = self.client.query(query).result_rows

            trending = []
            for row in results:
                trending.append({
                    "podcast_id": row[0],
                    "downloads": row[1]
                })

            return trending

        except Exception as e:
            logger.error(f"Error querying trending: {e}")
            return []

    async def get_engagement_metrics(
        self,
        podcast_id: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """Get engagement metrics."""
        try:
            query = f"""
                SELECT
                    countIf(event_type = 'play') as plays,
                    countIf(event_type = 'completion') as completions,
                    round(completions / plays * 100, 2) as completion_rate
                FROM events
                WHERE podcast_id = '{podcast_id}'
                AND date BETWEEN '{start_date}' AND '{end_date}'
            """

            results = self.client.query(query).result_rows

            if results:
                row = results[0]
                return {
                    "plays": row[0],
                    "completions": row[1],
                    "completion_rate": row[2]
                }

            return {}

        except Exception as e:
            logger.error(f"Error querying engagement metrics: {e}")
            return {}

    async def get_realtime_dashboard(self) -> Dict:
        """Get real-time dashboard data."""
        try:
            # Last hour activity
            query = """
                SELECT
                    event_type,
                    count(*) as count
                FROM events
                WHERE timestamp >= now() - INTERVAL 1 HOUR
                GROUP BY event_type
            """

            results = self.client.query(query).result_rows
            activity = {row[0]: row[1] for row in results}

            return {
                "last_hour": activity,
                "active_now": activity.get("play", 0)
            }

        except Exception as e:
            logger.error(f"Error querying realtime dashboard: {e}")
            return {}
