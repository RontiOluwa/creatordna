# =============================================================================
# app/publisher.py — ingestion-service
# =============================================================================
# Publishes VideoIngested events to RabbitMQ.
# Connection is managed by shared/rabbitmq/client.py.
# =============================================================================

import logging
from shared.rabbitmq.client import publish
from shared.schemas.events import VideoIngested

logger = logging.getLogger(__name__)

ROUTING_KEY = "video.ingested"


async def publish_video_ingested(
    video_id: str,
    handle: str,
    description: str,
    revenue: str,
    revenue_raw: float,
    items_sold: int,
    views: int,
    gpm: str,
    niche: str,
    category_id: str,
):
    """
    Publish a VideoIngested event after a new video is inserted.
    Consumed by analysis-service to trigger angle extraction.
    """
    event = VideoIngested(
        video_id=video_id,
        handle=handle or "",
        description=description or "",
        revenue=revenue or "",
        revenue_raw=revenue_raw,
        items_sold=items_sold,
        views=views,
        gpm=gpm,
        niche=niche,
        category_id=category_id,
    )
    await publish(ROUTING_KEY, event.model_dump_json().encode())
    logger.debug(f"Published video.ingested: {video_id}")
