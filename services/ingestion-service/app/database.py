# =============================================================================
# app/database.py
# =============================================================================
# Database connection and table setup for the ingestion service.
#
# Tables owned by this service:
#   raw_videos   — every TikTok Shop video pulled from Kalodata
#   scrape_runs  — audit log of every ingestion run (success/failure)
#
# SQLAlchemy is used for connection pooling and table creation only.
# Raw SQL (psycopg2) is used for inserts to keep things simple and fast.
# =============================================================================

import psycopg2
import psycopg2.pool
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Connection pool — reuses connections instead of opening a new one per insert
_pool: psycopg2.pool.SimpleConnectionPool = None


def init_pool():
    """
    Initialise the connection pool.
    Called once at service startup from main.py lifespan.
    """
    global _pool
    _pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )
    logger.info("Database connection pool initialised")


def get_conn():
    """Borrow a connection from the pool."""
    return _pool.getconn()


def release_conn(conn):
    """Return a connection to the pool."""
    _pool.putconn(conn)


def create_tables():
    """
    Create all tables this service owns if they don't already exist.
    Safe to run on every startup — uses IF NOT EXISTS.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            -- Stores raw TikTok Shop video data from Kalodata
            CREATE TABLE IF NOT EXISTS raw_videos (
                id              BIGSERIAL PRIMARY KEY,
                tiktok_video_id TEXT UNIQUE,           -- dedup key
                handle          TEXT,                   -- creator TikTok handle
                description     TEXT,                   -- hook text / caption
                duration        TEXT,                   -- e.g. "42s"
                revenue         TEXT,                   -- formatted e.g. "$65.83k"
                revenue_raw     NUMERIC,                -- parsed numeric for sorting
                items_sold      INTEGER,
                views           BIGINT,
                gpm             TEXT,                   -- gross profit per 1000 views
                ad_cpa          TEXT,                   -- cost per acquisition
                ad_view_ratio   TEXT,
                ad_roas         TEXT,                   -- return on ad spend
                niche           TEXT,                   -- category name
                category_id     TEXT,                   -- Kalodata category ID
                revenue_trend   JSONB,                  -- daily revenue array
                views_trend     JSONB,                  -- daily views array
                raw_json        JSONB,                  -- full API response preserved
                scraped_at      TIMESTAMP DEFAULT NOW()
            );

            -- Audit log for every scrape run
            CREATE TABLE IF NOT EXISTS scrape_runs (
                id            BIGSERIAL PRIMARY KEY,
                category      TEXT,
                videos_found  INTEGER DEFAULT 0,
                videos_new    INTEGER DEFAULT 0,
                status        TEXT,    -- 'success' | 'error'
                error_message TEXT,
                ran_at        TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        logger.info("Database tables ready")
    finally:
        release_conn(conn)
