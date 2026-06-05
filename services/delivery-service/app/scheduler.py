# =============================================================================
# app/scheduler.py — delivery-service
# =============================================================================
# APScheduler setup for the delivery service.
#
# Runs the daily idea delivery for all active creators.
# Schedule: 7am UTC daily (configurable via env vars)
# =============================================================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def init_scheduler():
    """
    Register the daily delivery job and start the scheduler.
    Called once at service startup.
    """
    scheduler.add_job(
        _delivery_job,
        trigger=CronTrigger(
            hour=settings.DELIVERY_CRON_HOUR,
            minute=settings.DELIVERY_CRON_MINUTE,
        ),
        id="daily_delivery",
        name="Daily idea delivery",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — daily delivery at "
        f"{settings.DELIVERY_CRON_HOUR:02d}:"
        f"{settings.DELIVERY_CRON_MINUTE:02d} UTC"
    )


def shutdown_scheduler():
    """Shut down scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler shut down")


async def _delivery_job():
    """
    Async wrapper for the daily delivery run.
    Imports run_delivery here to avoid circular imports.
    """
    from app.routes.ideas import run_delivery
    try:
        logger.info("Scheduled delivery starting...")
        results = await run_delivery()
        total = sum(r.ideas_generated for r in results)
        logger.info(f"Scheduled delivery done — {total} ideas generated")
    except Exception as e:
        logger.error(f"Scheduled delivery failed: {e}", exc_info=True)
