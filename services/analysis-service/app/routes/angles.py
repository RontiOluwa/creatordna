# =============================================================================
# app/routes/angles.py
# =============================================================================
# HTTP endpoints for the analysis service.
#
# Routes:
#   GET /angles          — list all extracted angles with optional filters
#   GET /angles/:id      — get a single angle by ID
#   GET /angles/stats    — breakdown of angles by type and niche
# =============================================================================

from fastapi import APIRouter, HTTPException, Query
from app.database import get_conn, release_conn
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/angles", tags=["Angles"])


@router.get("")
async def list_angles(
    niche: Optional[str] = Query(None, description="Filter by niche"),
    angle_type: Optional[str] = Query(None, description="Filter by angle type"),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    """
    List extracted content angles with optional filters.

    Used by the delivery service to query the angle library
    when matching angles to creator profiles.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()

        # Build dynamic query based on filters
        conditions = []
        params = []

        if niche:
            conditions.append("source_niche = %s")
            params.append(niche)

        if angle_type:
            conditions.append("angle_type = %s")
            params.append(angle_type)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        cur.execute(f"""
            SELECT id, video_id, angle_name, angle_type,
                   hook_formula, hook_example, why_it_works,
                   best_for_niches, shot_list, cta,
                   source_handle, source_revenue, source_niche,
                   created_at
            FROM angles
            {where}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        angles = [dict(zip(columns, row)) for row in rows]

        # Convert datetime to string for JSON serialisation
        for angle in angles:
            if angle.get("created_at"):
                angle["created_at"] = str(angle["created_at"])

        cur.close()
        return {"angles": angles, "count": len(angles)}

    finally:
        release_conn(conn)


@router.get("/stats")
async def angle_stats():
    """
    Returns breakdown of angles by type and niche.
    Useful for monitoring extraction quality and coverage.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                angle_type,
                count(*) as count
            FROM angles
            GROUP BY angle_type
            ORDER BY count DESC
        """)
        by_type = [
            {"angle_type": row[0], "count": row[1]}
            for row in cur.fetchall()
        ]

        cur.execute("""
            SELECT
                source_niche,
                count(*) as count
            FROM angles
            GROUP BY source_niche
            ORDER BY count DESC
        """)
        by_niche = [
            {"niche": row[0], "count": row[1]}
            for row in cur.fetchall()
        ]

        cur.close()
        return {
            "total": sum(r["count"] for r in by_type),
            "by_type": by_type,
            "by_niche": by_niche,
        }

    finally:
        release_conn(conn)


@router.get("/{angle_id}")
async def get_angle(angle_id: int):
    """Get a single angle by its database ID."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, video_id, angle_name, angle_type,
                   hook_formula, hook_example, why_it_works,
                   best_for_niches, shot_list, cta,
                   source_handle, source_revenue, source_niche,
                   created_at
            FROM angles
            WHERE id = %s
        """, (angle_id,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Angle not found")

        columns = [desc[0] for desc in cur.description]
        angle = dict(zip(columns, row))
        if angle.get("created_at"):
            angle["created_at"] = str(angle["created_at"])

        cur.close()
        return angle

    finally:
        release_conn(conn)
