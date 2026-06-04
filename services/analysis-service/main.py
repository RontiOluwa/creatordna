from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.database import init_pool, close_pool
from shared.rabbitmq.client import init_rabbitmq, close_rabbitmq
from app.database import create_tables
from app.consumer import init_consumer, close_consumer
from app.routes.angles import router as angles_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Analysis service starting...")
    init_pool()
    create_tables()
    await init_rabbitmq(prefetch_count=1)
    await init_consumer()
    logger.info("Analysis service ready — consuming VideoIngested events")
    yield
    logger.info("Analysis service shutting down...")
    await close_consumer()
    await close_rabbitmq()
    close_pool()
    logger.info("Analysis service stopped")


app = FastAPI(title="SFN Analysis Service", version="0.2.0", lifespan=lifespan)
app.include_router(angles_router)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "analysis-service"}


@app.get("/")
async def root():
    return {"service": "analysis-service", "version": "0.2.0"}
