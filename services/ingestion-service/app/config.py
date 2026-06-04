# =============================================================================
# app/config.py
# =============================================================================
# Centralised settings for the ingestion service.
# All environment variables are read once here and imported everywhere else.
# Using pydantic-settings means values are validated at startup — the service
# fails fast with a clear error if a required variable is missing.
# =============================================================================

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    # ── Database ──────────────────────────────────────────────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "sfn"
    DB_USER: str = "sfn_user"
    DB_PASSWORD: str = "sfn_pass"

    @property
    def database_url(self) -> str:
        """SQLAlchemy-compatible connection string."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ── RabbitMQ ──────────────────────────────────────────────────────────────
    RABBITMQ_URL: str = "amqp://sfn:sfn_pass@localhost:5672/"

    # ── Kalodata ──────────────────────────────────────────────────────────────
    # Session cookie — expires when browser session ends.
    # Refresh via DevTools → Network → queryList → Headers → Cookie
    KALODATA_COOKIE: str = ""

    # ── Scraper config ────────────────────────────────────────────────────────
    # How many seconds to wait between category requests (be polite)
    SCRAPE_DELAY_SECONDS: int = 2

    # Date range for video data (last 30 days)
    SCRAPE_START_DATE: str = "2026-05-04"
    SCRAPE_END_DATE: str = "2026-06-02"

    # ── Scheduler ─────────────────────────────────────────────────────────────
    # Cron schedule for daily ingestion run (default: 2am UTC daily)
    INGEST_CRON_HOUR: int = 2
    INGEST_CRON_MINUTE: int = 0

    class Config:
        env_file = ".env"
        extra = "ignore"


# Single instance imported everywhere
settings = Settings()
