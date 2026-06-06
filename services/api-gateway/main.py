# =============================================================================
# services/api-gateway/main.py
# =============================================================================

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from shared.database import init_pool, close_pool
from shared.rabbitmq.client import init_rabbitmq, close_rabbitmq
from app.database import create_tables
from app.routes.auth import router as auth_router
from app.routes.creators import router as creators_router
from app.routes.ideas import router as ideas_router
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
    version="0.3.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(creators_router)
app.include_router(ideas_router)


# ── Validation error handler ──────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"].replace("Value error, ", ""),
        })
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": errors}
    )


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/", tags=["System"])
async def root():
    return {"service": "api-gateway", "version": "0.3.0"}
