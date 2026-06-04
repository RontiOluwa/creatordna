from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoIngested(BaseModel):
    video_id: str
    handle: str
    description: str
    revenue: str
    revenue_raw: Optional[float]
    items_sold: Optional[int]
    views: Optional[int]
    gpm: Optional[str]
    niche: str
    category_id: str
    ingested_at: datetime = datetime.now()

class AngleExtracted(BaseModel):
    video_id: str
    angle_name: str
    angle_type: str
    hook_formula: str
    hook_example: str
    why_it_works: str
    best_for_niches: list[str]
    shot_list: list[str]
    cta: str
    extracted_at: datetime = datetime.now()

class IdeaDelivered(BaseModel):
    creator_id: str
    idea_id: str
    hook: str
    shot_list: list[str]
    cta: str
    delivered_at: datetime = datetime.now()
