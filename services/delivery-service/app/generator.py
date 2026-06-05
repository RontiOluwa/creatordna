# =============================================================================
# app/generator.py — delivery-service
# =============================================================================
# Claude-powered content idea generator.
#
# Takes a creator's DNA profile and matched angles, sends them to Claude,
# and gets back personalised content ideas written in the creator's voice.
#
# This is the core personalisation engine — what makes ideas feel like
# they were written specifically for each creator rather than generic
# output from a content template.
# =============================================================================

import json
import logging
import anthropic
from app.config import settings
from app.models import CreatorContext, AngleContext, GeneratedIdea

logger = logging.getLogger(__name__)

_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _build_generation_prompt(
    creator: CreatorContext,
    angles: list[AngleContext],
) -> str:
    """
    Build the idea generation prompt for Claude.

    The prompt gives Claude:
    1. The creator's full DNA profile — tone, style, audience, niche
    2. A set of proven angle formulas from viral videos
    3. Instructions to write ideas IN THE CREATOR'S VOICE

    The key difference from generic content generation:
    Claude is told to adapt the angle formula to this specific creator's
    style — not just copy the hook example from the angle library.
    """
    angles_text = ""
    for i, angle in enumerate(angles, 1):
        angles_text += f"""
Angle {i}: {angle.angle_name} [{angle.angle_type}]
  Formula: {angle.hook_formula}
  Example: {angle.hook_example}
  Why it works: {angle.why_it_works}
  Proof revenue: {angle.source_revenue}
  Shot list: {json.dumps(angle.shot_list)}
  CTA: {angle.cta}
"""

    return f"""You are a TikTok Shop content strategist generating personalised content ideas for a specific creator.

CREATOR PROFILE:
- Handle: @{creator.tiktok_handle}
- Primary niche: {creator.primary_niche}
- Tone: {creator.tone}
- Hook style: {creator.hook_style}
- Content style: {creator.content_style}
- Audience: {creator.audience_type}
- Avg video length: {creator.avg_video_length}
- Content patterns: {json.dumps(creator.raw_dna.get('content_patterns', []))}
- Strong topics: {json.dumps(creator.raw_dna.get('strong_topics', []))}
- Avoid topics: {json.dumps(creator.raw_dna.get('avoid_topics', []))}

PROVEN ANGLE FORMULAS (from viral TikTok Shop videos):
{angles_text}

TASK:
Generate {settings.IDEAS_PER_CREATOR} personalised content ideas for @{creator.tiktok_handle}.

For each idea:
1. Pick the most suitable angle formula
2. Adapt the hook to match the creator's tone and style — do NOT just copy the example
3. Write a shot list tailored to their content style ({creator.content_style})
4. Write a CTA suited to their audience ({creator.audience_type})

Respond with a JSON array of exactly {settings.IDEAS_PER_CREATOR} ideas:
[
  {{
    "hook": "the personalised hook written in creator's voice",
    "shot_list": ["shot 1", "shot 2", "shot 3"],
    "cta": "personalised call to action",
    "angle_type": "the angle type used",
    "angle_index": 1,
    "source_revenue": "revenue of proof video",
    "why_this_works": "1 sentence on why this fits this creator"
  }}
]

Respond with valid JSON array only. No markdown, no extra text."""


async def generate_ideas(
    creator: CreatorContext,
    angles: list[AngleContext],
) -> list[GeneratedIdea]:
    """
    Generate personalised content ideas for a creator using Claude.

    Args:
        creator : CreatorContext with full DNA profile
        angles  : matched angles from the angle library

    Returns:
        list of GeneratedIdea — personalised and ready to deliver
    """
    if not angles:
        logger.warning(f"No angles available for @{creator.tiktok_handle}")
        return []

    logger.info(
        f"Generating {settings.IDEAS_PER_CREATOR} ideas "
        f"for @{creator.tiktok_handle}"
    )

    prompt = _build_generation_prompt(creator, angles)

    message = _client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=settings.CLAUDE_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]).strip()

    ideas_data = json.loads(raw)

    # Convert to GeneratedIdea objects
    ideas = []
    for item in ideas_data:
        # Map angle_index back to actual angle ID
        angle_index = item.get("angle_index", 1) - 1
        angle = angles[min(angle_index, len(angles) - 1)]

        ideas.append(GeneratedIdea(
            hook=item["hook"],
            shot_list=item["shot_list"],
            cta=item["cta"],
            angle_type=item.get("angle_type", angle.angle_type),
            angle_id=angle.angle_id,
            source_revenue=item.get("source_revenue", angle.source_revenue),
            why_this_works=item.get("why_this_works", ""),
        ))

    logger.info(
        f"Generated {len(ideas)} ideas for @{creator.tiktok_handle}"
    )
    return ideas
