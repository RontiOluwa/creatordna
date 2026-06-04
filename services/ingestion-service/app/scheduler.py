# =============================================================================
# app/scheduler.py
# =============================================================================
# APScheduler setup for the ingestion service.
#
# Runs run_full_scrape() on a daily cron schedule.
# Schedule is configured via environment variables:
#   INGEST_CRON_HOUR   (default: 2)
#   INGEST_CRON_MINUTE (default: 0)
#
# This means by default the scraper runs at 2:00am UTC every day,
# well within Kalodata's daily search reset window.
# =============================================================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.scraper import run_full_scrape
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Single scheduler instance
scheduler = AsyncIOScheduler()


def init_scheduler():
    """
    Register the daily scrape job and start the scheduler.
    Called once at service startup from main.py lifespan.
    """
    scheduler.add_job(
        _scrape_job,
        trigger=CronTrigger(
            hour=settings.INGEST_CRON_HOUR,
            minute=settings.INGEST_CRON_MINUTE,
        ),
        id="daily_scrape",
        name="Daily Kalodata scrape",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — daily scrape at "
        f"{settings.INGEST_CRON_HOUR:02d}:{settings.INGEST_CRON_MINUTE:02d} UTC"
    )


def shutdown_scheduler():
    """Shut down scheduler gracefully — waits for running jobs to finish."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler shut down")


async def _scrape_job():
    """
    Async wrapper around run_full_scrape.
    APScheduler calls this on the cron schedule.
    Errors are caught and logged — never crash the scheduler.
    """
    try:
        logger.info("Scheduled scrape starting...")
        results = run_full_scrape()
        total = sum(r.videos_new for r in results)
        logger.info(f"Scheduled scrape done — {total} new videos")
    except Exception as e:
        logger.error(f"Scheduled scrape failed: {e}")
