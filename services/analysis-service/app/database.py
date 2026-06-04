# =============================================================================
# app/database.py — analysis-service
# =============================================================================
# Table creation for the analysis service.
# Connection pooling is handled by shared/database.py.
#
# Tables owned by this service:
#   angles — extracted content angles from Claude analysis
# =============================================================================

import logging
from shared.database import get_conn, release_conn

logger = logging.getLogger(__name__)


def create_tables():
    """
    Create all tables owned by the analysis service.
    Safe to run on every startup — uses IF NOT EXISTS.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS angles (
                id              BIGSERIAL PRIMARY KEY,
                video_id        TEXT,
                angle_name      TEXT,
                angle_type      TEXT,
                hook_formula    TEXT,
                hook_example    TEXT,
                why_it_works    TEXT,
                best_for_niches JSONB,
                shot_list       JSONB,
                cta             TEXT,
                source_handle   TEXT,
                source_revenue  TEXT,
                source_niche    TEXT,
                created_at      TIMESTAMP DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_angles_niche
                ON angles (source_niche);

            CREATE INDEX IF NOT EXISTS idx_angles_type
                ON angles (angle_type);
        """)
        conn.commit()
        cur.close()
        logger.info("Analysis tables ready")
    finally:
        release_conn(conn)
