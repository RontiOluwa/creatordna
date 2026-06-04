# =============================================================================
# app/config.py
# =============================================================================
# Centralised settings for the analysis service.
# Reads all values from environment variables / .env file automatically.
# =============================================================================

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ── Database ──────────────────────────────────────────────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "sfn"
    DB_USER: str = "sfn_user"
    DB_PASSWORD: str = "sfn_pass"

    # ── RabbitMQ ──────────────────────────────────────────────────────────────
    RABBITMQ_URL: str = "amqp://sfn:sfn_pass@localhost:5672/"

    # ── Anthropic ─────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""

    # ── Analysis config ───────────────────────────────────────────────────────
    # Claude model to use for angle extraction
    CLAUDE_MODEL: str = "claude-sonnet-4-6"

    # Max tokens for angle extraction response
    CLAUDE_MAX_TOKENS: int = 1000

    # How many concurrent Claude calls to allow
    MAX_CONCURRENT_EXTRACTIONS: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
