# =============================================================================
# app/database.py — ingestion-service
# =============================================================================
# Table creation for the ingestion service.
# Connection pooling is handled by shared/database.py.
#
# Tables owned by this service:
#   raw_videos  — TikTok Shop videos pulled from Kalodata
#   scrape_runs — audit log of every ingestion run
# =============================================================================

import logging
from shared.database import get_conn, release_conn

logger = logging.getLogger(__name__)


def create_tables():
    """
    Create all tables owned by the ingestion service.
    Safe to run on every startup — uses IF NOT EXISTS.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_videos (
                id              BIGSERIAL PRIMARY KEY,
                tiktok_video_id TEXT UNIQUE,
                handle          TEXT,
                description     TEXT,
                duration        TEXT,
                revenue         TEXT,
                revenue_raw     NUMERIC,
                items_sold      INTEGER,
                views           BIGINT,
                gpm             TEXT,
                ad_cpa          TEXT,
                ad_view_ratio   TEXT,
                ad_roas         TEXT,
                niche           TEXT,
                category_id     TEXT,
                revenue_trend   JSONB,
                views_trend     JSONB,
                raw_json        JSONB,
                scraped_at      TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS scrape_runs (
                id            BIGSERIAL PRIMARY KEY,
                category      TEXT,
                videos_found  INTEGER DEFAULT 0,
                videos_new    INTEGER DEFAULT 0,
                status        TEXT,
                error_message TEXT,
                ran_at        TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        logger.info("Ingestion tables ready")
    finally:
        release_conn(conn)
