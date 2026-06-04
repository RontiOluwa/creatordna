# =============================================================================
# app/extractor.py
# =============================================================================
# Claude-powered content angle extractor.
#
# Responsibilities:
#   - Build a prompt from VideoIngested event data
#   - Call Claude API via Anthropic SDK
#   - Parse and validate the JSON response
#   - Return a structured ExtractedAngle object
#
# This is the core AI logic of the analysis service — ported and
# productionised from the Phase 0 Jupyter notebook validation.
# =============================================================================

import json
import logging
import anthropic
from app.config import settings
from app.models import ExtractedAngle

logger = logging.getLogger(__name__)

# Initialise Anthropic client once at module load
_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# The 6 angle types the model can assign
ANGLE_TYPES = [
    "problem_agitate_solve",
    "social_proof",
    "urgency_deal",
    "curiosity_gap",
    "transformation",
    "demonstration",
]


def _build_prompt(
    description: str,
    revenue: str,
    items_sold: int,
    views: int,
    gpm: str,
    niche: str,
) -> str:
    """
    Build the angle extraction prompt for Claude.

    The prompt is designed to extract reusable, actionable content angles
    rather than just summarising the video. Each angle must include a
    hook formula that other creators can adapt to their own niche.
    """
    return f"""You are a TikTok Shop content strategist. Analyze this top-performing video and extract a reusable content angle.

VIDEO DATA:
- Hook/Description: {description}
- Revenue Generated: {revenue}
- Items Sold: {items_sold}
- Views: {views}
- GPM (revenue per 1000 views): {gpm}
- Niche: {niche}

Extract a structured content angle from this video. Respond in this exact JSON format:
{{
  "angle_name": "short name for this angle (3-5 words)",
  "angle_type": "one of: problem_agitate_solve, social_proof, urgency_deal, curiosity_gap, transformation, demonstration",
  "hook_formula": "the reusable hook pattern extracted from this video — use [brackets] for variable parts",
  "hook_example": "a fresh example hook using this formula for the same niche",
  "why_it_works": "1-2 sentences on the psychology behind why this converts",
  "best_for_niches": ["niche1", "niche2", "niche3"],
  "shot_list": ["shot 1 description", "shot 2 description", "shot 3 description"],
  "cta": "recommended call to action"
}}

Respond with valid JSON only. No markdown, no extra text, no code fences."""


def _parse_response(raw: str) -> ExtractedAngle:
    """
    Parse Claude's response into an ExtractedAngle object.

    Handles the case where Claude wraps the JSON in markdown code fences
    despite being told not to — a common model behaviour.
    """
    text = raw.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        text = "\n".join(lines[1:-1]).strip()

    data = json.loads(text)
    return ExtractedAngle(**data)


async def extract_angle(
    video_id: str,
    description: str,
    revenue: str,
    items_sold: int,
    views: int,
    gpm: str,
    niche: str,
    handle: str,
) -> ExtractedAngle:
    """
    Extract a content angle from a TikTok Shop video using Claude.

    This is the main entry point called by the RabbitMQ consumer
    for each VideoIngested event.

    Args:
        video_id    : tiktok_video_id for logging/tracking
        description : hook text / caption
        revenue     : formatted revenue string e.g. "$65.83k"
        items_sold  : number of items sold
        views       : total view count
        gpm         : gross profit per 1000 views
        niche       : category name e.g. "beauty_skincare"
        handle      : creator TikTok handle

    Returns:
        ExtractedAngle with all fields populated

    Raises:
        Exception if Claude API call fails or response cannot be parsed
    """
    logger.info(f"Extracting angle for video {video_id} ({niche})")

    prompt = _build_prompt(
        description=description,
        revenue=revenue,
        items_sold=items_sold or 0,
        views=views or 0,
        gpm=gpm or "N/A",
        niche=niche,
    )

    message = _client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=settings.CLAUDE_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    angle = _parse_response(raw)

    logger.info(
        f"Extracted angle for {video_id}: "
        f"'{angle.angle_name}' [{angle.angle_type}]"
    )
    return angle
