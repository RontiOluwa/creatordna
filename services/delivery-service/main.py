# =============================================================================
# services/delivery-service/main.py
# =============================================================================
# Delivery Service — generates and delivers daily content ideas.
#
# Startup sequence:
#   1. Initialise shared DB pool
#   2. Connect to shared RabbitMQ
#   3. Start daily delivery scheduler
# =============================================================================

from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.database import init_pool, close_pool
from shared.rabbitmq.client import init_rabbitmq, close_rabbitmq
from app.scheduler import init_scheduler, shutdown_scheduler
from app.routes.ideas import router as ideas_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Delivery service starting...")
    init_pool()
    await init_rabbitmq(prefetch_count=10)
    init_scheduler()
    logger.info("Delivery service ready")
    yield
    logger.info("Delivery service shutting down...")
    shutdown_scheduler()
    await close_rabbitmq()
    close_pool()
    logger.info("Delivery service stopped")


app = FastAPI(
    title="SFN Delivery Service",
    description="Generates and delivers daily personalised content ideas",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(ideas_router)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "delivery-service"}


@app.get("/", tags=["System"])
async def root():
    return {"service": "delivery-service", "version": "0.2.0"}
