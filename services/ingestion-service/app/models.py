# =============================================================================
# app/models.py
# =============================================================================
# Internal Pydantic models for the ingestion service.
#
# These are NOT the shared RabbitMQ event schemas (those live in shared/).
# These are the internal data shapes used within this service:
#   - RawVideo     : a normalised video record ready for DB insert
#   - ScrapeResult : summary of a completed scrape run
# =============================================================================

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import Field


class RawVideo(BaseModel):
    """
    A normalised TikTok Shop video record.
    Created by the scraper after parsing the Kalodata API response.
    """
    tiktok_video_id: str
    handle: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    revenue: Optional[str] = None
    revenue_raw: Optional[float] = None      # parsed from "$65.83k" → 65830.0
    items_sold: Optional[int] = None
    views: Optional[int] = None
    gpm: Optional[str] = None
    ad_cpa: Optional[str] = None
    ad_view_ratio: Optional[str] = None
    ad_roas: Optional[str] = None
    niche: str                               # category name e.g. "beauty_skincare"
    category_id: str                         # Kalodata category ID
    revenue_trend: list = []
    views_trend: list = []
    raw_json: dict = {}


class ScrapeResult(BaseModel):
    """
    Summary of a completed category scrape run.
    Stored in scrape_runs table and returned by the /ingest/status endpoint.
    """
    category: str
    videos_found: int = 0
    videos_new: int = 0
    status: str                              # 'success' | 'error'
    error_message: Optional[str] = None
    ran_at: datetime = Field(default_factory=datetime.now)
