# =============================================================================
# app/routes/ingest.py
# =============================================================================
# HTTP endpoints for the ingestion service.
#
# These are internal endpoints — not exposed to creators.
# Used for manual triggering during development and monitoring in production.
#
# Routes:
#   POST /ingest/trigger                — manually run full scrape across all niches
#   POST /ingest/trigger/:category_name — scrape one specific niche by keyword
#   GET  /ingest/status                 — scheduler info and configured niches
# =============================================================================

from fastapi import APIRouter, HTTPException
from app.scraper import run_full_scrape, scrape_category, KEYWORDS
from app.scheduler import scheduler
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/trigger")
async def trigger_full_scrape():
    """
    Manually trigger a full scrape across all configured niches.

    Runs one keyword search per niche — uses your full daily
    Kalodata allowance (up to 10 searches).

    Runs synchronously — response returns after all niches are scraped.
    Use this during development to seed the database without waiting for cron.
    """
    logger.info("Manual full scrape triggered via API")
    results = run_full_scrape()

    return {
        "message": "Scrape complete",
        "results": [r.model_dump() for r in results],
        "total_new": sum(r.videos_new for r in results),
        "total_found": sum(r.videos_found for r in results),
    }


@router.post("/trigger/{category_name}")
async def trigger_category_scrape(category_name: str):
    """
    Manually trigger a scrape for one specific niche.

    Uses 1 of your 10 daily Kalodata searches.

    Args:
        category_name: must be one of the keys in KEYWORDS dict
                       e.g. "beauty_skincare", "fitness", "hair_care"
    """
    if category_name not in KEYWORDS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown category '{category_name}'. "
                f"Valid options: {list(KEYWORDS.keys())}"
            )
        )

    keyword = KEYWORDS[category_name]
    logger.info(
        f"Manual category scrape triggered: {category_name} (keyword='{keyword}')")
    result = scrape_category(category_name, keyword)

    return {
        "message": f"Scrape complete for {category_name}",
        "result": result.model_dump(),
    }


@router.get("/status")
async def scrape_status():
    """
    Returns scheduler info, next scheduled run time, and configured niches.
    Useful for monitoring in production and debugging during development.
    """
    jobs = scheduler.get_jobs()
    job_info = []

    for job in jobs:
        job_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
        })

    return {
        "scheduler_running": scheduler.running,
        "jobs": job_info,
        "niches_configured": list(KEYWORDS.keys()),
        "keywords": KEYWORDS,
    }
