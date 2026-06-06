# =============================================================================
# app/routes/ideas.py — api-gateway
# =============================================================================
# Proxy routes for ideas — forwards to delivery-service internally.
# All routes require JWT authentication.
# Internal requests to delivery-service include X-Internal-Secret header.
# =============================================================================

from fastapi import APIRouter, HTTPException, Depends
from app.auth import get_current_creator
from shared.database import get_conn, release_conn
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ideas", tags=["Ideas"])

DELIVERY_URL = os.getenv("DELIVERY_SERVICE_URL", "http://delivery-service:8003")
INTERNAL_SECRET = os.getenv("INTERNAL_SERVICE_SECRET", "")

INTERNAL_HEADERS = {"x-internal-secret": INTERNAL_SECRET}


async def _proxy_get(path: str) -> dict:
    """Forward GET to delivery service with internal auth header."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(
                f"{DELIVERY_URL}{path}",
                headers=INTERNAL_HEADERS,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Delivery service error: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Proxy GET error: {e}")
            raise HTTPException(status_code=503, detail="Delivery service unavailable")


async def _proxy_post(path: str) -> dict:
    """Forward POST to delivery service with internal auth header."""
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(
                f"{DELIVERY_URL}{path}",
                headers=INTERNAL_HEADERS,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Delivery failed: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Proxy POST error: {e}")
            raise HTTPException(status_code=503, detail="Delivery service unavailable")


@router.post("/deliver/me")
async def trigger_my_delivery(
    creator: dict = Depends(get_current_creator),
):
    """
    Trigger idea delivery for the authenticated creator.
    Rate limited to once per day — delivery service enforces this.
    """
    handle = creator["handle"]
    logger.info(f"Delivery triggered for @{handle}")
    return await _proxy_post(f"/ideas/deliver/{handle}")


@router.get("/stats/me")
async def get_my_stats(
    creator: dict = Depends(get_current_creator),
):
    """Get idea delivery stats for the authenticated creator."""
    creator_id = int(creator["sub"])
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                count(*) as total,
                count(*) FILTER (WHERE feedback = 'made_it') as made_it,
                count(*) FILTER (WHERE feedback IS NOT NULL) as rated,
                avg(
                    CASE
                        WHEN source_revenue ~ '\\$[0-9]+\\.?[0-9]*k'
                        THEN REPLACE(REPLACE(source_revenue,'$',''),'k','')::numeric * 1000
                        WHEN source_revenue ~ '\\$[0-9]+\\.?[0-9]*m'
                        THEN REPLACE(REPLACE(source_revenue,'$',''),'m','')::numeric * 1000000
                        ELSE NULL
                    END
                ) as avg_proof
            FROM content_ideas
            WHERE creator_id = %s
        """, (creator_id,))
        row = cur.fetchone()
        cur.close()

        total = row[0] or 0
        made_it = row[1] or 0
        rated = row[2] or 0
        avg_proof = row[3]
        hit_rate = round(made_it / rated * 100) if rated > 0 else 0

        if avg_proof:
            if avg_proof >= 1_000_000:
                avg_proof_str = f"${avg_proof/1_000_000:.1f}m"
            elif avg_proof >= 1_000:
                avg_proof_str = f"${avg_proof/1_000:.1f}k"
            else:
                avg_proof_str = f"${avg_proof:.0f}"
        else:
            avg_proof_str = "—"

        return {
            "total": total,
            "made_it": made_it,
            "hit_rate": f"{hit_rate}%" if rated > 0 else "—",
            "avg_proof": avg_proof_str,
        }
    finally:
        release_conn(conn)


@router.get("/streak/me")
async def get_my_streak(
    creator: dict = Depends(get_current_creator),
):
    """Calculate consecutive days with delivered ideas."""
    creator_id = int(creator["sub"])
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT delivered_at::date as day
            FROM content_ideas
            WHERE creator_id = %s
            ORDER BY day DESC
        """, (creator_id,))
        days = [row[0] for row in cur.fetchall()]
        cur.close()

        if not days:
            return {"streak": 0}

        from datetime import date, timedelta
        streak = 0
        today = date.today()
        for i, day in enumerate(days):
            expected = today - timedelta(days=i)
            if day == expected:
                streak += 1
            else:
                break

        return {"streak": streak}
    finally:
        release_conn(conn)


@router.get("/{creator_id}/today")
async def get_todays_ideas(
    creator_id: int,
    creator: dict = Depends(get_current_creator),
):
    """Get today's ideas. Creators can only view their own."""
    if str(creator_id) != creator["sub"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await _proxy_get(f"/ideas/{creator_id}/today")


@router.get("/{creator_id}")
async def get_all_ideas(
    creator_id: int,
    creator: dict = Depends(get_current_creator),
):
    """Get all ideas. Creators can only view their own."""
    if str(creator_id) != creator["sub"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await _proxy_get(f"/ideas/{creator_id}")
