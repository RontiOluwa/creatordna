# =============================================================================
# app/publisher.py
# =============================================================================
# RabbitMQ publisher for the ingestion service.
#
# Publishes VideoIngested events to the sfn.events exchange after each
# successful video insert. The analysis-service consumes these events
# and triggers angle extraction for each new video.
#
# Exchange design:
#   Type    : topic (allows routing by pattern e.g. "video.*", "angle.*")
#   Name    : sfn.events
#   Durable : true (survives RabbitMQ restarts)
#
# Routing keys published by this service:
#   video.ingested  → consumed by analysis-service
# =============================================================================

import aio_pika
import json
import logging
from app.config import settings
from shared.schemas.events import VideoIngested

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "sfn.events"
ROUTING_KEY = "video.ingested"

# Module-level connection and channel — initialised at startup
_connection: aio_pika.RobustConnection = None
_channel: aio_pika.Channel = None
_exchange: aio_pika.Exchange = None


async def init_publisher():
    """
    Connect to RabbitMQ and declare the sfn.events exchange.
    Called once at service startup from main.py lifespan.

    Uses connect_robust which automatically reconnects if the
    connection drops — important for long-running services.
    """
    global _connection, _channel, _exchange

    _connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    _channel = await _connection.channel()

    # Declare the exchange — idempotent, safe to call on every startup
    _exchange = await _channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.TOPIC,
        durable=True,   # survives RabbitMQ restarts
    )
    logger.info(f"RabbitMQ publisher ready — exchange: {EXCHANGE_NAME}")


async def close_publisher():
    """Close RabbitMQ connection gracefully on service shutdown."""
    if _connection and not _connection.is_closed:
        await _connection.close()
        logger.info("RabbitMQ publisher connection closed")


async def publish_video_ingested(video_id: str, handle: str, description: str,
                                 revenue: str, revenue_raw: float,
                                 items_sold: int, views: int, gpm: str,
                                 niche: str, category_id: str):
    """
    Publish a VideoIngested event to RabbitMQ.

    Called by the scraper after each successful DB insert.
    The analysis-service picks this up and runs angle extraction.

    Args:
        video_id    : tiktok_video_id (dedup key)
        handle      : creator TikTok handle
        description : hook text / caption
        revenue     : formatted revenue string e.g. "$65.83k"
        revenue_raw : parsed numeric revenue
        items_sold  : number of items sold
        views       : total view count
        gpm         : gross profit per 1000 views
        niche       : category name e.g. "beauty_skincare"
        category_id : Kalodata category ID
    """
    if not _exchange:
        logger.warning("Publisher not initialised — skipping event")
        return

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

    message = aio_pika.Message(
        body=event.model_dump_json().encode(),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # survives RabbitMQ restart
    )

    await _exchange.publish(message, routing_key=ROUTING_KEY)
    logger.debug(f"Published video.ingested: {video_id}")
