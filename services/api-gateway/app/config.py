# =============================================================================
# app/config.py — api-gateway
# =============================================================================
# Centralised settings for the api-gateway service.
# =============================================================================

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ── Anthropic ─────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET: str = "change_this_to_a_random_secret"
    JWT_EXPIRY_HOURS: int = 24

    # ── App ───────────────────────────────────────────────────────────────────
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
