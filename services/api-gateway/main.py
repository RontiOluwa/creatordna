# =============================================================================
# services/api-gateway/main.py
# =============================================================================
# API Gateway — the single public-facing entry point for all client requests.
#
# Responsibilities:
#   - JWT authentication and token validation
#   - Request routing to internal microservices
#   - Rate limiting via Redis
#   - Creator registration and login
#
# Port: 8000
#
# All frontend requests hit this service first. Internal services
# (ingestion, analysis, delivery) are NOT directly exposed to the internet.
# =============================================================================

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Configure logging — all services use the same format for easy log aggregation
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
      - Connect to Redis for rate limiting (Phase 6)
      - Initialize JWT middleware (Phase 6)

    On shutdown:
      - Close Redis connection gracefully
    """
    logger.info("API Gateway starting up...")
    # TODO Phase 6: initialize Redis connection
    # TODO Phase 6: initialize JWT middleware
    yield
    logger.info("API Gateway shutting down...")
    # TODO Phase 6: close Redis connection


app = FastAPI(
    title="SFN API Gateway",
    description="Public-facing entry point for the SFN platform",
    version="0.1.0",
    # Disable docs in production — enable only in development
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """
    Health check endpoint.
    Used by Docker healthcheck and load balancers to verify the service is up.
    """
    return {"status": "ok", "service": "api-gateway"}


@app.get("/", tags=["System"])
async def root():
    """Root endpoint — returns service info."""
    return {"service": "api-gateway", "version": "0.1.0"}


# ── Placeholder Routes (implemented in later phases) ─────────────────────────

# Phase 6 will add:
#   POST /auth/register     — creator signup with TikTok handle
#   POST /auth/login        — returns JWT token
#   GET  /ideas/today       — fetch today's personalized content ideas
#   GET  /ideas/history     — paginated idea history
#   GET  /profile           — creator DNA profile
#   POST /feedback          — creator rates an idea (feeds personalization)
