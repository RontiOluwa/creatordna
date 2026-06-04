# =============================================================================
# services/delivery-service/main.py
# =============================================================================
# Delivery Service — generates and delivers daily content ideas to creators.
#
# Responsibilities:
#   - Run a daily cron job for each active creator (7am their timezone)
#   - Load the creator's content DNA profile from postgres
#   - Query the angle library for top-matching angles by niche and style
#   - Send creator profile + matched angles to Claude to generate
#     a personalized content idea (hook, shot list, CTA, proof video)
#   - Store the generated idea in the content_ideas postgres table
#   - Publish an IdeaDelivered event to RabbitMQ
#
# Port: 8003
#
# Event flow:
#   Daily cron → delivery-service → postgres (creator_profiles + angles)
#                                 → Claude API (personalization)
#                                 → postgres (content_ideas)
#                                 → RabbitMQ (idea.delivered)
#                                               ↓
#                                  notification-service (consumes)
#
# RabbitMQ:
#   Publishes: sfn.events → idea.delivered
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
      - Initialize APScheduler for daily idea delivery cron
      - Initialize Anthropic client for idea personalization

    On shutdown:
      - Shut down scheduler gracefully (finish running jobs)
      - Close RabbitMQ and Anthropic connections
    """
    logger.info("Delivery service starting up...")
    # TODO Phase 5: connect to RabbitMQ
    # TODO Phase 5: initialize APScheduler
    # TODO Phase 5: initialize Anthropic client
    yield
    logger.info("Delivery service shutting down...")
    # TODO Phase 5: shutdown scheduler and close connections


app = FastAPI(
    title="SFN Delivery Service",
    description="Generates and delivers daily personalized content ideas to creators",
    version="0.1.0",
    docs_url="/docs",
)


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """
    Health check endpoint.
    Returns ok when the service is running and the scheduler is active.
    """
    return {"status": "ok", "service": "delivery-service"}


@app.get("/", tags=["System"])
async def root():
    """Root endpoint — returns service info."""
    return {"service": "delivery-service", "version": "0.1.0"}


# ── Placeholder Routes (implemented in Phase 5) ───────────────────────────────

# Phase 5 will add:
#   POST /deliver/trigger/:creator_id  — manually trigger idea generation (dev)
#   GET  /ideas/:creator_id            — list all ideas for a creator
#   GET  /scheduler/status             — next run time, last run, errors
