# =============================================================================
# app/routes/ideas.py — delivery-service
# =============================================================================
# HTTP endpoints and core delivery logic.
#
# Routes:
#   POST /ideas/deliver           — manually trigger delivery for all creators
#   POST /ideas/deliver/:handle   — trigger delivery for one creator
#   GET  /ideas/:creator_id       — get all ideas for a creator
#   GET  /ideas/:creator_id/today — get today's ideas for a creator
# =============================================================================

from fastapi import APIRouter, HTTPException
from app.models import CreatorContext, DeliveryResult
from app.matcher import match_angles
from app.generator import generate_ideas
from app.database import (
    get_active_creators, save_idea,
    get_conn, release_conn
)
from app.config import settings
from shared.rabbitmq.client import publish
from shared.schemas.events import IdeaDelivered
import json
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ideas", tags=["Ideas"])


async def deliver_to_creator(creator: dict) -> DeliveryResult:
    """
    Full delivery pipeline for one creator:
      1. Build CreatorContext from DB row
      2. Match angles from library
      3. Generate personalised ideas via Claude
      4. Save ideas to DB
      5. Publish IdeaDelivered events

    Args:
        creator: dict from get_active_creators()

    Returns:
        DeliveryResult with status and idea count
    """
    handle = creator["tiktok_handle"]
    creator_id = creator["id"]

    try:
        # 1. Build context
        context = CreatorContext(
            creator_id=creator_id,
            tiktok_handle=handle,
            primary_niche=creator["primary_niche"] or "general",
            secondary_niches=creator["secondary_niches"] or [],
            tone=creator["tone"] or "casual_humor",
            hook_style=creator["hook_style"] or "statement",
            avg_video_length=creator["avg_video_length"] or "30s",
            audience_type=creator["audience_type"] or "general",
            content_style=creator["content_style"] or "talking_head",
            raw_dna=creator["raw_dna"] or {},
        )

        # 2. Match angles
        angles = match_angles(context)
        if not angles:
            logger.warning(f"No angles found for @{handle}")
            return DeliveryResult(
                creator_id=creator_id,
                tiktok_handle=handle,
                ideas_generated=0,
                status="error",
                error_message="No matching angles found",
            )

        # 3. Generate personalised ideas
        ideas = await generate_ideas(context, angles)
        if not ideas:
            return DeliveryResult(
                creator_id=creator_id,
                tiktok_handle=handle,
                ideas_generated=0,
                status="error",
                error_message="Idea generation returned empty",
            )

        # 4. Save ideas + publish events
        saved = 0
        for idea in ideas:
            idea_id = save_idea(
                creator_id=creator_id,
                angle_id=idea.angle_id,
                hook=idea.hook,
                shot_list=idea.shot_list,
                cta=idea.cta,
                angle_type=idea.angle_type,
                source_revenue=idea.source_revenue,
            )

            # 5. Publish IdeaDelivered event
            event = IdeaDelivered(
                creator_id=str(creator_id),
                idea_id=str(idea_id),
                hook=idea.hook,
                shot_list=idea.shot_list,
                cta=idea.cta,
                angle_type=idea.angle_type,
            )
            await publish(
                "idea.delivered",
                event.model_dump_json().encode()
            )
            saved += 1

        logger.info(f"Delivered {saved} ideas to @{handle}")
        return DeliveryResult(
            creator_id=creator_id,
            tiktok_handle=handle,
            ideas_generated=saved,
            status="success",
        )

    except Exception as e:
        logger.error(f"Delivery failed for @{handle}: {e}", exc_info=True)
        return DeliveryResult(
            creator_id=creator_id,
            tiktok_handle=handle,
            ideas_generated=0,
            status="error",
            error_message=str(e),
        )


async def run_delivery() -> list[DeliveryResult]:
    """
    Run delivery for all active creators.
    Called by scheduler daily and by POST /ideas/deliver manually.
    """
    creators = get_active_creators()
    logger.info(f"Starting delivery for {len(creators)} active creators")

    results = []
    for creator in creators:
        result = await deliver_to_creator(creator)
        results.append(result)

    total = sum(r.ideas_generated for r in results)
    logger.info(f"Delivery complete — {total} ideas generated")
    return results


# ── HTTP Endpoints ────────────────────────────────────────────────────────────

@router.post("/deliver")
async def trigger_full_delivery():
    """
    Manually trigger delivery for all active creators.
    Useful during development without waiting for 7am cron.
    """
    logger.info("Manual full delivery triggered")
    results = await run_delivery()
    return {
        "message": "Delivery complete",
        "results": [r.model_dump() for r in results],
        "total_ideas": sum(r.ideas_generated for r in results),
        "creators_served": len([r for r in results if r.status == "success"]),
    }


@router.post("/deliver/{handle}")
async def trigger_creator_delivery(handle: str):
    """
    Manually trigger delivery for one specific creator.
    """
    handle = handle.lstrip("@").lower().strip()

    creators = get_active_creators()
    creator = next(
        (c for c in creators if c["tiktok_handle"] == handle),
        None
    )

    if not creator:
        raise HTTPException(
            status_code=404,
            detail=f"Creator @{handle} not found or has no DNA profile"
        )

    result = await deliver_to_creator(creator)
    return {
        "message": f"Delivery complete for @{handle}",
        "result": result.model_dump(),
    }


@router.get("/{creator_id}")
async def get_creator_ideas(creator_id: int, limit: int = 20):
    """Get all content ideas for a creator."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                id, hook, shot_list, cta,
                angle_type, source_revenue,
                feedback, delivered_at
            FROM content_ideas
            WHERE creator_id = %s
            ORDER BY delivered_at DESC
            LIMIT %s
        """, (creator_id, limit))
        rows = cur.fetchall()
        columns = [
            "id", "hook", "shot_list", "cta",
            "angle_type", "source_revenue",
            "feedback", "delivered_at"
        ]
        ideas = [dict(zip(columns, row)) for row in rows]
        for idea in ideas:
            idea["delivered_at"] = str(idea["delivered_at"])
        cur.close()
        return {"ideas": ideas, "count": len(ideas)}
    finally:
        release_conn(conn)


@router.get("/{creator_id}/today")
async def get_todays_ideas(creator_id: int):
    """Get today's content ideas for a creator."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                id, hook, shot_list, cta,
                angle_type, source_revenue,
                feedback, delivered_at
            FROM content_ideas
            WHERE creator_id = %s
            AND delivered_at::date = CURRENT_DATE
            ORDER BY delivered_at DESC
        """, (creator_id,))
        rows = cur.fetchall()
        columns = [
            "id", "hook", "shot_list", "cta",
            "angle_type", "source_revenue",
            "feedback", "delivered_at"
        ]
        ideas = [dict(zip(columns, row)) for row in rows]
        for idea in ideas:
            idea["delivered_at"] = str(idea["delivered_at"])
        cur.close()
        return {"ideas": ideas, "count": len(ideas)}
    finally:
        release_conn(conn)
