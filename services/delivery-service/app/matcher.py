# =============================================================================
# app/matcher.py — delivery-service
# =============================================================================
# Angle matching logic with fallback strategy.
# =============================================================================

import logging
from app.models import CreatorContext, AngleContext
from app.database import get_angles_for_niche, get_angles_cross_niche
from app.config import settings
from shared.database import get_conn, release_conn

logger = logging.getLogger(__name__)


def get_any_angles(limit: int) -> list[dict]:
    """
    Fallback — fetch top angles from any niche.
    Used when creator niche has no matching angles.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                id, angle_name, angle_type,
                hook_formula, hook_example,
                why_it_works, shot_list, cta,
                source_revenue, source_niche
            FROM angles
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        columns = [
            "id", "angle_name", "angle_type",
            "hook_formula", "hook_example",
            "why_it_works", "shot_list", "cta",
            "source_revenue", "source_niche"
        ]
        cur.close()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        release_conn(conn)


def match_angles(creator: CreatorContext) -> list[AngleContext]:
    """
    Find the best matching angles for a creator.
    Falls back to any available angles if niche has no matches.
    """
    limit = settings.TOP_ANGLES_TO_MATCH
    logger.info(
        f"Matching angles for @{creator.tiktok_handle} "
        f"(niche={creator.primary_niche})"
    )

    # 1. Primary niche
    primary_angles = get_angles_for_niche(creator.primary_niche, limit=limit)
    logger.info(
        f"  Found {len(primary_angles)} angles "
        f"for primary niche '{creator.primary_niche}'"
    )

    # 2. Cross-niche fill
    if len(primary_angles) < limit and creator.secondary_niches:
        needed = limit - len(primary_angles)
        cross = get_angles_cross_niche(creator.secondary_niches, limit=needed)
        existing_ids = {a["id"] for a in primary_angles}
        cross = [a for a in cross if a["id"] not in existing_ids]
        primary_angles.extend(cross)
        logger.info(f"  Added {len(cross)} cross-niche angles")

    # 3. General fallback — any angles from the library
    if not primary_angles:
        logger.warning(
            f"  No niche match for '{creator.primary_niche}' "
            f"— falling back to general angle pool"
        )
        primary_angles = get_any_angles(limit)
        logger.info(f"  Fallback: found {len(primary_angles)} general angles")

    # 4. Diversity filter
    diverse = _diversify(primary_angles)

    # 5. Convert to AngleContext
    result = []
    for a in diverse[:limit]:
        result.append(AngleContext(
            angle_id=a["id"],
            angle_name=a["angle_name"],
            angle_type=a["angle_type"],
            hook_formula=a["hook_formula"],
            hook_example=a["hook_example"],
            why_it_works=a["why_it_works"],
            shot_list=a["shot_list"] if isinstance(a["shot_list"], list) else [],
            cta=a["cta"],
            source_revenue=a["source_revenue"] or "",
            source_niche=a["source_niche"] or "",
        ))

    logger.info(f"  Matched {len(result)} angles for @{creator.tiktok_handle}")
    return result


def _diversify(angles: list[dict]) -> list[dict]:
    """Max 2 of same angle type for variety."""
    type_count: dict[str, int] = {}
    diverse = []
    for angle in angles:
        atype = angle.get("angle_type", "")
        count = type_count.get(atype, 0)
        if count < 2:
            diverse.append(angle)
            type_count[atype] = count + 1
    return diverse
