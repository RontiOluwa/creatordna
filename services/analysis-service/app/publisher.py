# =============================================================================
# app/publisher.py — analysis-service
# =============================================================================
# Publishes AngleExtracted events to RabbitMQ.
# Connection is managed by shared/rabbitmq/client.py.
# =============================================================================

import logging
from shared.rabbitmq.client import publish
from shared.schemas.events import AngleExtracted

logger = logging.getLogger(__name__)

ROUTING_KEY = "angle.extracted"


async def publish_angle_extracted(
    video_id: str,
    angle_name: str,
    angle_type: str,
    hook_formula: str,
    hook_example: str,
    why_it_works: str,
    best_for_niches: list,
    shot_list: list,
    cta: str,
):
    """
    Publish an AngleExtracted event after a new angle is inserted.
    Consumed by delivery-service to build the angle library.
    """
    event = AngleExtracted(
        video_id=video_id,
        angle_name=angle_name,
        angle_type=angle_type,
        hook_formula=hook_formula,
        hook_example=hook_example,
        why_it_works=why_it_works,
        best_for_niches=best_for_niches,
        shot_list=shot_list,
        cta=cta,
    )
    await publish(ROUTING_KEY, event.model_dump_json().encode())
    logger.debug(f"Published angle.extracted: {video_id}")
