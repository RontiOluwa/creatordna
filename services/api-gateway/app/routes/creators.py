# =============================================================================
# app/routes/creators.py — api-gateway
# =============================================================================
# Creator onboarding and profile endpoints.
# Protected routes require a valid JWT token.
# =============================================================================

from fastapi import APIRouter, HTTPException, Depends
from app.models import CreatorOnboardRequest, FeedbackRequest, OnboardResponse
from app.profiler import build_creator_dna
from app.auth import get_current_creator
from shared.database import get_conn, release_conn
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/creators", tags=["Creators"])


@router.post("/onboard", response_model=OnboardResponse)
async def onboard_creator(
    request: CreatorOnboardRequest,
    creator: dict = Depends(get_current_creator),   # 🔒 requires JWT
):
    """
    Complete creator onboarding — build DNA profile.
    Requires authentication. Creator can only onboard themselves.
    """
    handle = request.tiktok_handle.lstrip("@").lower().strip()

    # Creators can only onboard their own handle
    if handle != creator["handle"]:
        raise HTTPException(
            status_code=403,
            detail="You can only onboard your own TikTok handle"
        )

    logger.info(f"Onboarding creator: @{handle}")

    conn = get_conn()
    try:
        cur = conn.cursor()

        # Check if already onboarded
        cur.execute(
            "SELECT id FROM creator_profiles WHERE tiktok_handle = %s",
            (handle,)
        )
        if cur.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"@{handle} is already onboarded"
            )

        creator_id = int(creator["sub"])

    except HTTPException:
        raise
    finally:
        release_conn(conn)

    # Build DNA profile via Claude
    try:
        dna = await build_creator_dna(handle, request.video_urls)
    except Exception as e:
        logger.error(f"DNA profiling failed for @{handle}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"DNA profiling failed: {str(e)}"
        )

    # Store DNA profile
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO creator_profiles (
                creator_id, tiktok_handle,
                primary_niche, secondary_niches,
                tone, hook_style, avg_video_length,
                audience_type, content_style,
                posting_frequency, submitted_videos, raw_dna
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            creator_id,
            handle,
            dna.primary_niche,
            json.dumps(dna.secondary_niches),
            dna.tone,
            dna.hook_style,
            dna.avg_video_length,
            dna.audience_type,
            dna.content_style,
            dna.posting_frequency,
            json.dumps(request.video_urls),
            json.dumps(dna.raw_dna),
        ))
        conn.commit()
        cur.close()
        logger.info(f"DNA profile stored for @{handle}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to store DNA profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to store profile")
    finally:
        release_conn(conn)

    return OnboardResponse(
        creator_id=creator_id,
        tiktok_handle=handle,
        dna=dna,
    )


@router.get("/me")
async def get_my_profile(creator: dict = Depends(get_current_creator)):
    """
    Get own creator profile. Requires authentication.
    """
    handle = creator["handle"]
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, tiktok_handle, email, is_active, created_at
            FROM creators
            WHERE tiktok_handle = %s
        """, (handle,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Creator not found")
        cur.close()
        return {
            "id": row[0],
            "tiktok_handle": row[1],
            "email": row[2],
            "is_active": row[3],
            "created_at": str(row[4]),
        }
    finally:
        release_conn(conn)


@router.get("/me/dna")
async def get_my_dna(creator: dict = Depends(get_current_creator)):
    """
    Get own DNA profile. Requires authentication.
    """
    handle = creator["handle"]
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                cp.primary_niche, cp.secondary_niches,
                cp.tone, cp.hook_style, cp.avg_video_length,
                cp.audience_type, cp.content_style,
                cp.posting_frequency, cp.raw_dna, cp.updated_at
            FROM creator_profiles cp
            WHERE cp.tiktok_handle = %s
            ORDER BY cp.updated_at DESC
            LIMIT 1
        """, (handle,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail="No DNA profile found — complete onboarding first"
            )
        cur.close()
        return {
            "tiktok_handle": handle,
            "primary_niche": row[0],
            "secondary_niches": row[1],
            "tone": row[2],
            "hook_style": row[3],
            "avg_video_length": row[4],
            "audience_type": row[5],
            "content_style": row[6],
            "posting_frequency": row[7],
            "raw_dna": row[8],
            "updated_at": str(row[9]),
        }
    finally:
        release_conn(conn)


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    creator: dict = Depends(get_current_creator),   # 🔒 requires JWT
):
    """
    Submit feedback on a delivered content idea.
    Creators can only feedback on their own ideas.
    """
    creator_id = int(creator["sub"])
    conn = get_conn()
    try:
        cur = conn.cursor()

        # Verify idea belongs to this creator
        cur.execute("""
            SELECT id FROM content_ideas
            WHERE id = %s AND creator_id = %s
        """, (request.idea_id, creator_id))

        if not cur.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Idea not found or does not belong to you"
            )

        cur.execute("""
            UPDATE content_ideas
            SET feedback = %s
            WHERE id = %s
            RETURNING id
        """, (request.feedback, request.idea_id))

        conn.commit()
        cur.close()
        return {
            "message": "Feedback recorded",
            "idea_id": request.idea_id,
            "feedback": request.feedback,
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        release_conn(conn)
