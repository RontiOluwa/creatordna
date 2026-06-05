# =============================================================================
# app/database.py — delivery-service
# =============================================================================
# Table queries for the delivery service.
# Connection pooling is handled by shared/database.py.
#
# This service reads from:
#   creator_profiles — to get creator DNA
#   angles           — to get the angle library
#   creators         — to get active creators
#
# This service writes to:
#   content_ideas    — generated ideas per creator
# =============================================================================

import logging
from shared.database import get_conn, release_conn

logger = logging.getLogger(__name__)


def get_active_creators() -> list[dict]:
    """
    Fetch all active creators with their DNA profiles.
    Called by the scheduler every morning to get the delivery list.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                c.id,
                c.tiktok_handle,
                cp.primary_niche,
                cp.secondary_niches,
                cp.tone,
                cp.hook_style,
                cp.avg_video_length,
                cp.audience_type,
                cp.content_style,
                cp.raw_dna
            FROM creators c
            JOIN creator_profiles cp ON cp.creator_id = c.id
            WHERE c.is_active = TRUE
            ORDER BY c.id
        """)
        rows = cur.fetchall()
        columns = [
            "id", "tiktok_handle", "primary_niche", "secondary_niches",
            "tone", "hook_style", "avg_video_length", "audience_type",
            "content_style", "raw_dna"
        ]
        cur.close()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        release_conn(conn)


def get_angles_for_niche(niche: str, limit: int = 10) -> list[dict]:
    """
    Fetch top angles matching a creator's primary niche.
    Used by the matcher to find relevant angles for personalisation.
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
            WHERE source_niche = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (niche, limit))
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


def get_angles_cross_niche(niches: list[str], limit: int = 5) -> list[dict]:
    """
    Fetch angles that work across multiple niches.
    Used as fallback when primary niche has few angles.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        placeholders = ",".join(["%s"] * len(niches))
        cur.execute(f"""
            SELECT
                id, angle_name, angle_type,
                hook_formula, hook_example,
                why_it_works, shot_list, cta,
                source_revenue, source_niche
            FROM angles
            WHERE source_niche IN ({placeholders})
            ORDER BY created_at DESC
            LIMIT %s
        """, niches + [limit])
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


def save_idea(
    creator_id: int,
    angle_id: int,
    hook: str,
    shot_list: list,
    cta: str,
    angle_type: str,
    source_revenue: str,
) -> int:
    """
    Save a generated content idea to the content_ideas table.
    Returns the new idea ID.
    """
    import json
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO content_ideas (
                creator_id, angle_id, hook,
                shot_list, cta, angle_type, source_revenue
            ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            creator_id,
            angle_id,
            hook,
            json.dumps(shot_list),
            cta,
            angle_type,
            source_revenue,
        ))
        idea_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return idea_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to save idea: {e}")
        raise
    finally:
        release_conn(conn)
