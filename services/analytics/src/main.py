"""Analytics Service - Metrics collection and reporting."""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging

from .collectors.event_collector import EventCollector
from .processors.metrics_processor import MetricsProcessor
from .queries.analytics_queries import AnalyticsQueries

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PodTranslate Analytics",
    version="1.0.0",
    description="Analytics collection and reporting service"
)

# Initialize services
event_collector = EventCollector()
metrics_processor = MetricsProcessor()
analytics_queries = AnalyticsQueries()


# Request models
class AnalyticsEvent(BaseModel):
    event_type: str  # download, play, completion, share, etc.
    podcast_id: str
    episode_id: Optional[str] = None
    language: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict] = {}


class AnalyticsQuery(BaseModel):
    podcast_id: Optional[str] = None
    episode_id: Optional[str] = None
    start_date: str
    end_date: str
    metrics: List[str]  # downloads, plays, completions, engagement
    group_by: Optional[str] = "day"  # hour, day, week, month


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "analytics",
        "version": "1.0.0"
    }


# Track event
@app.post("/track")
async def track_event(event: AnalyticsEvent):
    """
    Track an analytics event.

    Events are collected and batched for processing.
    """
    try:
        logger.info(f"Tracking event: {event.event_type}")

        await event_collector.collect(
            event_type=event.event_type,
            podcast_id=event.podcast_id,
            episode_id=event.episode_id,
            language=event.language,
            user_id=event.user_id,
            metadata=event.metadata
        )

        return {
            "success": True,
            "message": "Event tracked successfully"
        }

    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get podcast analytics
@app.get("/podcasts/{podcast_id}")
async def get_podcast_analytics(
    podcast_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    group_by: str = Query("day", description="Grouping: hour, day, week, month")
):
    """
    Get analytics for a podcast.

    Returns metrics like downloads, plays, completions by language and region.
    """
    try:
        logger.info(f"Fetching analytics for podcast: {podcast_id}")

        analytics = await analytics_queries.get_podcast_metrics(
            podcast_id=podcast_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )

        return {
            "podcast_id": podcast_id,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "metrics": analytics
        }

    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get episode analytics
@app.get("/episodes/{episode_id}")
async def get_episode_analytics(
    episode_id: str,
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """
    Get analytics for a specific episode.
    """
    try:
        logger.info(f"Fetching analytics for episode: {episode_id}")

        analytics = await analytics_queries.get_episode_metrics(
            episode_id=episode_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "episode_id": episode_id,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "metrics": analytics
        }

    except Exception as e:
        logger.error(f"Error fetching episode analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get language performance
@app.get("/podcasts/{podcast_id}/languages")
async def get_language_performance(
    podcast_id: str,
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """
    Get performance metrics by language.
    """
    try:
        logger.info(f"Fetching language performance for: {podcast_id}")

        performance = await analytics_queries.get_language_performance(
            podcast_id=podcast_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "podcast_id": podcast_id,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "languages": performance
        }

    except Exception as e:
        logger.error(f"Error fetching language performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get geographic distribution
@app.get("/podcasts/{podcast_id}/geography")
async def get_geographic_distribution(
    podcast_id: str,
    start_date: str = Query(...),
    end_date: str = Query(...),
    language: Optional[str] = Query(None)
):
    """
    Get geographic distribution of listeners.
    """
    try:
        logger.info(f"Fetching geographic data for: {podcast_id}")

        geography = await analytics_queries.get_geographic_distribution(
            podcast_id=podcast_id,
            start_date=start_date,
            end_date=end_date,
            language=language
        )

        return {
            "podcast_id": podcast_id,
            "language": language,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "geography": geography
        }

    except Exception as e:
        logger.error(f"Error fetching geographic data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get trending content
@app.get("/trending")
async def get_trending_content(
    period: str = Query("7d", description="Period: 1d, 7d, 30d"),
    language: Optional[str] = Query(None),
    limit: int = Query(10, le=100)
):
    """
    Get trending podcasts and episodes.
    """
    try:
        logger.info(f"Fetching trending content for period: {period}")

        trending = await analytics_queries.get_trending(
            period=period,
            language=language,
            limit=limit
        )

        return {
            "period": period,
            "language": language,
            "trending": trending
        }

    except Exception as e:
        logger.error(f"Error fetching trending content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get engagement metrics
@app.get("/podcasts/{podcast_id}/engagement")
async def get_engagement_metrics(
    podcast_id: str,
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """
    Get engagement metrics (completion rate, average listen time, etc.).
    """
    try:
        logger.info(f"Fetching engagement metrics for: {podcast_id}")

        engagement = await analytics_queries.get_engagement_metrics(
            podcast_id=podcast_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "podcast_id": podcast_id,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "engagement": engagement
        }

    except Exception as e:
        logger.error(f"Error fetching engagement metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Real-time dashboard data
@app.get("/dashboard/realtime")
async def get_realtime_dashboard():
    """
    Get real-time dashboard data.

    Returns current active listeners, recent activity, etc.
    """
    try:
        dashboard_data = await analytics_queries.get_realtime_dashboard()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "data": dashboard_data
        }

    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3003)
