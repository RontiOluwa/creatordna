# =============================================================================
# services/api-gateway/main.py
# =============================================================================
# API Gateway — public-facing entry point.
#
# Startup sequence:
#   1. Initialise shared DB pool
#   2. Create tables
#   3. Connect to shared RabbitMQ
# =============================================================================

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.database import init_pool, close_pool
from shared.rabbitmq.client import init_rabbitmq, close_rabbitmq
from app.database import create_tables
from app.routes.creators import router as creators_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway starting...")
    init_pool()
    create_tables()
    await init_rabbitmq(prefetch_count=10)
    logger.info("API Gateway ready")
    yield
    logger.info("API Gateway shutting down...")
    await close_rabbitmq()
    close_pool()
    logger.info("API Gateway stopped")


app = FastAPI(
    title="SFN API Gateway",
    description="Public-facing entry point for the SFN platform",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(creators_router)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/", tags=["System"])
async def root():
    return {"service": "api-gateway", "version": "0.2.0"}


# ── Validation error handler ──────────────────────────────────────────────────


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """
    Returns clear, human-readable validation errors instead of
    Pydantic's default verbose error format.
    """
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"].replace("Value error, ", ""),
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": errors,
        }
    )
