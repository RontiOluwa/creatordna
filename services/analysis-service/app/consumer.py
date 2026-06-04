# =============================================================================
# app/consumer.py — analysis-service
# =============================================================================
# RabbitMQ consumer for VideoIngested events.
# Connection is managed by shared/rabbitmq/client.py.
# =============================================================================

import json
import logging
import aio_pika
from shared.rabbitmq.client import get_channel, get_exchange
from shared.database import get_conn, release_conn
from shared.schemas.events import VideoIngested
from app.extractor import extract_angle
from app.publisher import publish_angle_extracted

logger = logging.getLogger(__name__)

QUEUE_NAME = "analysis.video.ingested"
ROUTING_KEY = "video.ingested"


async def init_consumer():
    """
    Declare queue, bind to exchange, and start consuming.
    Relies on shared RabbitMQ connection being initialised first.
    """
    channel = get_channel()
    exchange = get_exchange()

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=ROUTING_KEY)
    await queue.consume(process_message)

    logger.info(f"Consumer ready — queue={QUEUE_NAME} key={ROUTING_KEY}")


async def close_consumer():
    """Consumer cleanup — connection handled by shared client."""
    logger.info("Consumer stopped")


def _insert_angle(angle_data: dict) -> bool:
    """Insert extracted angle into the angles table."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO angles (
                video_id, angle_name, angle_type,
                hook_formula, hook_example, why_it_works,
                best_for_niches, shot_list, cta,
                source_handle, source_revenue, source_niche
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            angle_data["video_id"],
            angle_data["angle_name"],
            angle_data["angle_type"],
            angle_data["hook_formula"],
            angle_data["hook_example"],
            angle_data["why_it_works"],
            json.dumps(angle_data["best_for_niches"]),
            json.dumps(angle_data["shot_list"]),
            angle_data["cta"],
            angle_data["source_handle"],
            angle_data["source_revenue"],
            angle_data["source_niche"],
        ))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Angle insert failed: {e}")
        return False
    finally:
        release_conn(conn)


async def process_message(message: aio_pika.IncomingMessage):
    """
    Process a single VideoIngested message.
    Pipeline: deserialise → extract → insert → publish → ack
    On failure: nack and requeue.
    """
    async with message.process(requeue=True):
        try:
            event = VideoIngested.model_validate_json(message.body)
            logger.info(
                f"Processing {event.video_id} "
                f"({event.niche}) — '{event.description[:50]}'"
            )

            angle = await extract_angle(
                video_id=event.video_id,
                description=event.description,
                revenue=event.revenue,
                items_sold=event.items_sold,
                views=event.views,
                gpm=event.gpm,
                niche=event.niche,
                handle=event.handle,
            )

            inserted = _insert_angle({
                "video_id": event.video_id,
                "angle_name": angle.angle_name,
                "angle_type": angle.angle_type,
                "hook_formula": angle.hook_formula,
                "hook_example": angle.hook_example,
                "why_it_works": angle.why_it_works,
                "best_for_niches": angle.best_for_niches,
                "shot_list": angle.shot_list,
                "cta": angle.cta,
                "source_handle": event.handle,
                "source_revenue": event.revenue,
                "source_niche": event.niche,
            })

            if inserted:
                await publish_angle_extracted(
                    video_id=event.video_id,
                    angle_name=angle.angle_name,
                    angle_type=angle.angle_type,
                    hook_formula=angle.hook_formula,
                    hook_example=angle.hook_example,
                    why_it_works=angle.why_it_works,
                    best_for_niches=angle.best_for_niches,
                    shot_list=angle.shot_list,
                    cta=angle.cta,
                )
                logger.info(
                    f"Done: '{angle.angle_name}' "
                    f"[{angle.angle_type}] for {event.video_id}"
                )

        except Exception as e:
            logger.error(f"Failed to process message: {e}", exc_info=True)
