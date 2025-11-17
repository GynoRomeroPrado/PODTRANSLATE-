"""Webhook system for event notifications."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
import httpx
import hashlib
import hmac
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class WebhookConfig(BaseModel):
    """Webhook configuration."""
    url: HttpUrl
    events: List[str]  # List of event types to subscribe to
    secret: Optional[str] = None  # Secret for signature validation
    is_active: bool = True


class WebhookEvent(BaseModel):
    """Webhook event payload."""
    event_type: str
    timestamp: str
    data: Dict


# In-memory webhook storage (use database in production)
webhooks: Dict[str, WebhookConfig] = {}


@router.post("/webhooks")
async def create_webhook(webhook: WebhookConfig):
    """
    Register a new webhook endpoint.

    Args:
        webhook: Webhook configuration

    Returns:
        Webhook ID and configuration
    """
    import uuid

    webhook_id = str(uuid.uuid4())
    webhooks[webhook_id] = webhook

    logger.info(f"Webhook registered: {webhook_id}")

    return {
        "webhook_id": webhook_id,
        "url": str(webhook.url),
        "events": webhook.events,
        "is_active": webhook.is_active
    }


@router.get("/webhooks")
async def list_webhooks():
    """List all registered webhooks."""
    return {
        "webhooks": [
            {"id": wid, **wh.dict()}
            for wid, wh in webhooks.items()
        ]
    }


@router.get("/webhooks/{webhook_id}")
async def get_webhook(webhook_id: str):
    """Get webhook details."""
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {"id": webhook_id, **webhooks[webhook_id].dict()}


@router.put("/webhooks/{webhook_id}")
async def update_webhook(webhook_id: str, webhook: WebhookConfig):
    """Update webhook configuration."""
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhooks[webhook_id] = webhook

    return {"id": webhook_id, **webhook.dict()}


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Delete a webhook."""
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")

    del webhooks[webhook_id]

    return {"message": "Webhook deleted"}


@router.post("/webhooks/test/{webhook_id}")
async def test_webhook(webhook_id: str, background_tasks: BackgroundTasks):
    """Send a test event to webhook."""
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook = webhooks[webhook_id]

    test_event = WebhookEvent(
        event_type="test.ping",
        timestamp=datetime.utcnow().isoformat(),
        data={"message": "This is a test webhook"}
    )

    background_tasks.add_task(
        send_webhook_event,
        webhook,
        test_event
    )

    return {"message": "Test webhook sent"}


async def send_webhook_event(webhook: WebhookConfig, event: WebhookEvent):
    """
    Send an event to a webhook endpoint.

    Args:
        webhook: Webhook configuration
        event: Event to send
    """
    if not webhook.is_active:
        logger.debug(f"Webhook inactive, skipping: {webhook.url}")
        return

    if event.event_type not in webhook.events:
        logger.debug(f"Event {event.event_type} not subscribed, skipping")
        return

    try:
        payload = event.dict()
        payload_json = json.dumps(payload)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "PodTranslate-Webhook/1.0"
        }

        # Add signature if secret is configured
        if webhook.secret:
            signature = hmac.new(
                webhook.secret.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        # Send webhook
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                str(webhook.url),
                content=payload_json,
                headers=headers
            )

            response.raise_for_status()

            logger.info(f"Webhook sent successfully: {webhook.url}")

    except httpx.HTTPError as e:
        logger.error(f"Webhook delivery failed: {webhook.url} - {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending webhook: {e}")


async def trigger_webhook_event(event_type: str, data: Dict):
    """
    Trigger webhook event for all subscribed webhooks.

    Args:
        event_type: Type of event
        data: Event data
    """
    event = WebhookEvent(
        event_type=event_type,
        timestamp=datetime.utcnow().isoformat(),
        data=data
    )

    # Find all webhooks subscribed to this event
    for webhook in webhooks.values():
        if event_type in webhook.events and webhook.is_active:
            await send_webhook_event(webhook, event)


# Event types
WEBHOOK_EVENTS = {
    "transcription.started": "Transcription job started",
    "transcription.completed": "Transcription job completed",
    "transcription.failed": "Transcription job failed",
    "translation.completed": "Translation completed",
    "distribution.published": "Episode published to platform",
    "distribution.failed": "Distribution failed",
    "analytics.daily_report": "Daily analytics report",
    "user.created": "New user registered",
    "podcast.created": "New podcast created",
    "episode.created": "New episode created"
}


@router.get("/webhooks/events")
async def list_event_types():
    """List all available webhook event types."""
    return {
        "events": [
            {"type": event_type, "description": description}
            for event_type, description in WEBHOOK_EVENTS.items()
        ]
    }
