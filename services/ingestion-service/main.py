from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.database import init_pool, close_pool
from shared.rabbitmq.client import init_rabbitmq, close_rabbitmq
from app.database import create_tables
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
    logger.info("Ingestion service starting...")
    init_pool()
    create_tables()
    await init_rabbitmq(prefetch_count=10)
    init_scheduler()
    logger.info("Ingestion service ready")
    yield
    logger.info("Ingestion service shutting down...")
    shutdown_scheduler()
    await close_rabbitmq()
    close_pool()
    logger.info("Ingestion service stopped")


app = FastAPI(title="SFN Ingestion Service", version="0.2.0", lifespan=lifespan)
app.include_router(ingest_router)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "ingestion-service"}


@app.get("/")
async def root():
    return {"service": "ingestion-service", "version": "0.2.0"}
