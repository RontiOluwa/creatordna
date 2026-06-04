# =============================================================================
# services/analysis-service/main.py
# =============================================================================
# Analysis Service — extracts structured content angles from ingested videos.
#
# Responsibilities:
#   - Consume VideoIngested events from RabbitMQ
#   - Send video data to Claude (Anthropic SDK) for angle extraction
#   - Parse and validate Claude's JSON response into an Angle object
#   - Store extracted angles in the angles postgres table
#   - Publish AngleExtracted events to RabbitMQ
#   - Handle retries and dead-letter queue for failed extractions
#
# Port: 8002
#
# Event flow:
#   RabbitMQ (video.ingested) → analysis-service → Claude API
#                                                 → postgres (angles)
#                                                 → RabbitMQ (angle.extracted)
#                                                               ↓
#                                                  delivery-service (consumes)
#
# RabbitMQ:
#   Consumes : sfn.events → video.ingested
#   Publishes: sfn.events → angle.extracted
# =============================================================================

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages startup and shutdown lifecycle.

    On startup:
      - Connect to RabbitMQ
      - Declare sfn.events exchange and video.ingested queue
      - Start consuming VideoIngested messages in the background

    On shutdown:
      - Stop consuming new messages
      - Wait for in-flight angle extractions to complete
      - Close RabbitMQ and Anthropic client connections
    """
    logger.info("Analysis service starting up...")
    # TODO Phase 3: connect to RabbitMQ
    # TODO Phase 3: declare queue and start consumer
    # TODO Phase 3: initialize Anthropic client
    yield
    logger.info("Analysis service shutting down...")
    # TODO Phase 3: cancel consumer and close connections


app = FastAPI(
    title="SFN Analysis Service",
    description="Consumes video events and extracts content angles using Claude",
    version="0.1.0",
    docs_url="/docs",
)


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """
    Health check endpoint.
    Returns ok when the service is running and consuming from RabbitMQ.
    """
    return {"status": "ok", "service": "analysis-service"}


@app.get("/", tags=["System"])
async def root():
    """Root endpoint — returns service info."""
    return {"service": "analysis-service", "version": "0.1.0"}


# ── Placeholder Routes (implemented in Phase 3) ───────────────────────────────

# Phase 3 will add:
#   GET  /angles            — list extracted angles with filters (niche, type)
#   GET  /angles/:id        — get a single angle by ID
#   POST /angles/reprocess  — re-run extraction on a specific video (dev/debug)
#   GET  /queue/status      — pending messages, processing rate, error count
