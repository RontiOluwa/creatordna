# =============================================================================
# app/routes/creators.py — api-gateway
# =============================================================================
# Creator onboarding and profile endpoints.
#
# Routes:
#   POST /creators/onboard     — register creator + build DNA profile
#   GET  /creators/:handle     — get creator profile
#   GET  /creators/:handle/dna — get creator DNA profile
#   POST /creators/feedback    — submit idea feedback
# =============================================================================

from fastapi import APIRouter, HTTPException
from app.models import CreatorOnboardRequest, FeedbackRequest, OnboardResponse
from app.profiler import build_creator_dna
from shared.database import get_conn, release_conn
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/creators", tags=["Creators"])


@router.post("/onboard", response_model=OnboardResponse)
async def onboard_creator(request: CreatorOnboardRequest):
    """
    Register a new creator and build their DNA profile.

    Steps:
      1. Check if creator already exists
      2. Insert creator record
      3. Fetch video metadata + call Claude for DNA profiling
      4. Store DNA profile
      5. Return creator ID + DNA

    The creator provides their TikTok handle and 3-15 video URLs.
    Claude analyses the video descriptions to build their content DNA.
    """
    handle = request.tiktok_handle.lstrip("@").lower().strip()
    logger.info(f"Onboarding creator: @{handle}")

    conn = get_conn()
    try:
        cur = conn.cursor()

        # 1. Check if already exists
        cur.execute(
            "SELECT id FROM creators WHERE tiktok_handle = %s",
            (handle,)
        )
        existing = cur.fetchone()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Creator @{handle} is already registered"
            )

        # 2. Insert creator record
        cur.execute("""
            INSERT INTO creators (tiktok_handle, email)
            VALUES (%s, %s)
            RETURNING id
        """, (handle, request.email))
        creator_id = cur.fetchone()[0]
        conn.commit()

        logger.info(f"Creator @{handle} registered with id={creator_id}")

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to register creator: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        release_conn(conn)

    # 3. Build DNA profile via Claude
    try:
        dna = await build_creator_dna(handle, request.video_urls)
    except Exception as e:
        logger.error(f"DNA profiling failed for @{handle}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"DNA profiling failed: {str(e)}"
        )

    # 4. Store DNA profile
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
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )
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


@router.get("/{handle}")
async def get_creator(handle: str):
    """Get a creator record by TikTok handle."""
    handle = handle.lstrip("@").lower().strip()
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
            raise HTTPException(
                status_code=404,
                detail=f"Creator @{handle} not found"
            )
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


@router.get("/{handle}/dna")
async def get_creator_dna(handle: str):
    """Get a creator's DNA profile by TikTok handle."""
    handle = handle.lstrip("@").lower().strip()
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
            JOIN creators c ON c.id = cp.creator_id
            WHERE c.tiktok_handle = %s
            ORDER BY cp.updated_at DESC
            LIMIT 1
        """, (handle,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"No DNA profile found for @{handle}"
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
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on a delivered content idea.
    Stores the feedback for future DNA profile refinement.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE content_ideas
            SET feedback = %s
            WHERE id = %s
            RETURNING id
        """, (request.feedback, request.idea_id))
        updated = cur.fetchone()
        if not updated:
            raise HTTPException(
                status_code=404,
                detail=f"Idea {request.idea_id} not found"
            )
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
