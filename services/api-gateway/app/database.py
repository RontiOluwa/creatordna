# =============================================================================
# app/database.py — api-gateway
# =============================================================================
# Table creation for the api-gateway service.
# Connection pooling is handled by shared/database.py.
#
# Tables owned by this service:
#   creators          — registered creator accounts
#   creator_profiles  — Claude-generated DNA profiles
# =============================================================================

import logging
from shared.database import get_conn, release_conn

logger = logging.getLogger(__name__)


def create_tables():
    """
    Create all tables owned by the api-gateway.
    Safe to run on every startup — uses IF NOT EXISTS.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            -- Creator accounts
            CREATE TABLE IF NOT EXISTS creators (
                id              BIGSERIAL PRIMARY KEY,
                tiktok_handle   TEXT UNIQUE NOT NULL,
                email           TEXT UNIQUE,
                password_hash   TEXT,
                is_active       BOOLEAN DEFAULT TRUE,
                created_at      TIMESTAMP DEFAULT NOW(),
                updated_at      TIMESTAMP DEFAULT NOW()
            );

            -- Claude-generated DNA profiles
            -- One profile per creator, updated as feedback comes in
            CREATE TABLE IF NOT EXISTS creator_profiles (
                id              BIGSERIAL PRIMARY KEY,
                creator_id      BIGINT REFERENCES creators(id),
                tiktok_handle   TEXT NOT NULL,

                -- DNA fields extracted by Claude
                primary_niche   TEXT,
                secondary_niches JSONB DEFAULT '[]',
                tone            TEXT,   -- casual_humor | educational | inspirational
                hook_style      TEXT,   -- question_based | statement | story
                avg_video_length TEXT,
                audience_type   TEXT,
                content_style   TEXT,   -- talking_head | voiceover | text_only
                posting_frequency TEXT,

                -- Raw video data submitted during onboarding
                submitted_videos JSONB DEFAULT '[]',

                -- Full DNA JSON from Claude (for flexibility)
                raw_dna         JSONB DEFAULT '{}',

                created_at      TIMESTAMP DEFAULT NOW(),
                updated_at      TIMESTAMP DEFAULT NOW()
            );

            -- Content ideas delivered to creators
            CREATE TABLE IF NOT EXISTS content_ideas (
                id              BIGSERIAL PRIMARY KEY,
                creator_id      BIGINT REFERENCES creators(id),
                angle_id        BIGINT,
                hook            TEXT,
                shot_list       JSONB DEFAULT '[]',
                cta             TEXT,
                angle_type      TEXT,
                source_revenue  TEXT,
                feedback        TEXT,   -- 'made_it' | 'not_my_style' | NULL
                delivered_at    TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        logger.info("API Gateway tables ready")
    finally:
        release_conn(conn)
