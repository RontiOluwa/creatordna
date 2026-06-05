# =============================================================================
# app/config.py — delivery-service
# =============================================================================
# Centralised settings for the delivery service.
# =============================================================================

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ── Anthropic ─────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"
    CLAUDE_MAX_TOKENS: int = 2000

    # ── Delivery config ───────────────────────────────────────────────────────
    # How many ideas to generate per creator per day
    IDEAS_PER_CREATOR: int = 2

    # How many angles to pass to Claude for matching
    TOP_ANGLES_TO_MATCH: int = 5

    # Cron schedule — default 7am UTC daily
    DELIVERY_CRON_HOUR: int = 7
    DELIVERY_CRON_MINUTE: int = 0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
