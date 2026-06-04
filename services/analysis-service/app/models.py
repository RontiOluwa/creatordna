# =============================================================================
# app/models.py
# =============================================================================
# Internal Pydantic models for the analysis service.
# =============================================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExtractedAngle(BaseModel):
    """
    A structured content angle extracted by Claude from a TikTok Shop video.
    This is the core output of the analysis service.
    """
    angle_name: str
    angle_type: str         # problem_agitate_solve | social_proof | urgency_deal
                            # curiosity_gap | transformation | demonstration
    hook_formula: str       # reusable pattern e.g. "this [product] is different"
    hook_example: str       # fresh example using the formula
    why_it_works: str       # psychological explanation
    best_for_niches: list[str]
    shot_list: list[str]
    cta: str


class AngleRecord(BaseModel):
    """
    A complete angle record ready for database insertion.
    Combines ExtractedAngle with source video metadata.
    """
    video_id: str
    angle_name: str
    angle_type: str
    hook_formula: str
    hook_example: str
    why_it_works: str
    best_for_niches: list[str]
    shot_list: list[str]
    cta: str
    source_handle: Optional[str] = None
    source_revenue: Optional[str] = None
    source_niche: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
