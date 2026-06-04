# =============================================================================
# shared/database.py
# =============================================================================
# Shared PostgreSQL connection pool used by all microservices.
#
# Why shared?
#   Every service connects to the same Postgres instance with the same
#   credentials and the same pooling strategy. Centralising here means
#   one place to update connection logic across all services.
#
# Usage (in any service):
#   from shared.database import init_pool, get_conn, release_conn, create_tables
#
#   # In service startup (lifespan):
#   init_pool()
#
#   # In any function that needs DB:
#   conn = get_conn()
#   try:
#       cur = conn.cursor()
#       cur.execute("SELECT ...")
#       conn.commit()
#   finally:
#       release_conn(conn)
# =============================================================================

import psycopg2
import psycopg2.pool
import os
import logging

logger = logging.getLogger(__name__)

_pool: psycopg2.pool.SimpleConnectionPool = None


def init_pool(minconn: int = 1, maxconn: int = 10):
    """
    Initialise the shared connection pool.
    Called once at service startup from main.py lifespan.

    Reads connection details from environment variables directly
    so it works across all services without importing their config.

    Args:
        minconn: minimum connections to keep open (default 1)
        maxconn: maximum connections allowed (default 10)
    """
    global _pool
    _pool = psycopg2.pool.SimpleConnectionPool(
        minconn=minconn,
        maxconn=maxconn,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "sfn"),
        user=os.getenv("DB_USER", "sfn_user"),
        password=os.getenv("DB_PASSWORD", "sfn_pass"),
    )
    logger.info(
        f"Database pool initialised — "
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', 5432)}/"
        f"{os.getenv('DB_NAME', 'sfn')}"
    )


def get_conn() -> psycopg2.extensions.connection:
    """
    Borrow a connection from the pool.
    Always pair with release_conn() in a finally block.
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialised — call init_pool() first")
    return _pool.getconn()


def release_conn(conn: psycopg2.extensions.connection):
    """
    Return a connection to the pool.
    Call this in a finally block after every get_conn().
    """
    if _pool is not None:
        _pool.putconn(conn)


def close_pool():
    """
    Close all connections in the pool.
    Call this on service shutdown.
    """
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
        logger.info("Database pool closed")
