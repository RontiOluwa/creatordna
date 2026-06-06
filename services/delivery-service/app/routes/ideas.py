# =============================================================================
# app/routes/ideas.py — delivery-service
# =============================================================================

from fastapi import APIRouter, HTTPException, Depends
from app.models import CreatorContext, DeliveryResult
from app.matcher import match_angles
from app.generator import generate_ideas
from app.auth import verify_internal
from app.database import get_active_creators, save_idea, get_conn, release_conn
from app.config import settings
from shared.rabbitmq.client import publish
from shared.schemas.events import IdeaDelivered
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ideas", tags=["Ideas"])


def _already_delivered_today(creator_id: int) -> bool:
    """Check if ideas already delivered to this creator today."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT count(*) FROM content_ideas
            WHERE creator_id = %s
            AND delivered_at::date = CURRENT_DATE
        """, (creator_id,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    finally:
        release_conn(conn)


async def deliver_to_creator(creator: dict) -> DeliveryResult:
    """Full delivery pipeline for one creator."""
    handle = creator["tiktok_handle"]
    creator_id = creator["id"]

    try:
        # Skip if already delivered today
        if _already_delivered_today(creator_id):
            logger.info(f"@{handle} already has ideas today — skipping")
            return DeliveryResult(
                creator_id=creator_id,
                tiktok_handle=handle,
                ideas_generated=0,
                status="skipped",
                error_message="Already delivered today",
            )

        # Build context
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

        # Match angles
        angles = match_angles(context)
        if not angles:
            return DeliveryResult(
                creator_id=creator_id,
                tiktok_handle=handle,
                ideas_generated=0,
                status="error",
                error_message="No matching angles found",
            )

        # Generate ideas
        ideas = await generate_ideas(context, angles)
        if not ideas:
            return DeliveryResult(
                creator_id=creator_id,
                tiktok_handle=handle,
                ideas_generated=0,
                status="error",
                error_message="Idea generation returned empty",
            )

        # Save and publish
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
            event = IdeaDelivered(
                creator_id=str(creator_id),
                idea_id=str(idea_id),
                hook=idea.hook,
                shot_list=idea.shot_list,
                cta=idea.cta,
                angle_type=idea.angle_type,
            )
            await publish("idea.delivered", event.model_dump_json().encode())
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
    """Run delivery for all active creators."""
    creators = get_active_creators()
    logger.info(f"Starting delivery for {len(creators)} creators")
    results = []
    for creator in creators:
        result = await deliver_to_creator(creator)
        results.append(result)
    total = sum(r.ideas_generated for r in results)
    logger.info(f"Delivery complete — {total} ideas generated")
    return results


# ── HTTP Endpoints ────────────────────────────────────────────────────────────

@router.post("/deliver")
async def trigger_full_delivery(_: None = Depends(verify_internal)):
    """Trigger delivery for all active creators. Protected by internal secret."""
    logger.info("Full delivery triggered")
    results = await run_delivery()
    return {
        "message": "Delivery complete",
        "results": [r.model_dump() for r in results],
        "total_ideas": sum(r.ideas_generated for r in results),
        "creators_served": len([r for r in results if r.status == "success"]),
    }


@router.post("/deliver/{handle}")
async def trigger_creator_delivery(
    handle: str,
    _: None = Depends(verify_internal),
):
    """Trigger delivery for one creator. Protected by internal secret."""
    handle = handle.lstrip("@").lower().strip()
    creators = get_active_creators()
    creator = next(
        (c for c in creators if c["tiktok_handle"] == handle), None
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


@router.get("/{creator_id}/today")
async def get_todays_ideas(creator_id: int):
    """Get today's ideas for a creator."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, hook, shot_list, cta,
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


@router.get("/{creator_id}")
async def get_creator_ideas(creator_id: int, limit: int = 50):
    """Get all ideas for a creator."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, hook, shot_list, cta,
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
