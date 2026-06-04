# =============================================================================
# services/ingestion-service/main.py
# =============================================================================
# Ingestion Service — entry point.
#
# Startup sequence:
#   1. Initialise DB connection pool
#   2. Create tables (idempotent)
#   3. Connect to RabbitMQ and declare exchange
#   4. Start the daily scrape scheduler
#
# Shutdown sequence (on SIGTERM/SIGINT):
#   1. Stop scheduler (finish running jobs)
#   2. Close RabbitMQ connection
#   3. (DB pool closes automatically)
# =============================================================================

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_pool, create_tables
from app.publisher import init_publisher, close_publisher
from app.scheduler import init_scheduler, shutdown_scheduler
from app.routes.ingest import router as ingest_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Ingestion service starting...")

    # 1. Database
    init_pool()
    create_tables()

    # 2. RabbitMQ publisher
    await init_publisher()

    # 3. Scheduler
    init_scheduler()

    logger.info("Ingestion service ready")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Ingestion service shutting down...")
    shutdown_scheduler()
    await close_publisher()
    logger.info("Ingestion service stopped")


app = FastAPI(
    title="SFN Ingestion Service",
    description="Pulls TikTok Shop video data and publishes ingestion events",
    version="0.2.0",
    lifespan=lifespan,
)

# Register routes
app.include_router(ingest_router)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "ingestion-service"}


@app.get("/", tags=["System"])
async def root():
    return {"service": "ingestion-service", "version": "0.2.0"}
