# =============================================================================
# app/profiler.py — api-gateway
# =============================================================================
# Claude-powered creator DNA profiler.
#
# Responsibilities:
#   - Accept a list of TikTok video URLs from the creator
#   - Fetch basic metadata from each URL (title, description, hashtags)
#   - Send all video data to Claude for style analysis
#   - Return a structured CreatorDNA object
#
# Note on TikTok data:
#   We use a simple HTTP fetch to extract Open Graph metadata from each
#   TikTok URL. This gives us the video description and hashtags without
#   needing API access or scraping JavaScript-rendered content.
# =============================================================================

import httpx
import re
import json
import logging
import anthropic
from app.config import settings
from app.models import CreatorDNA

logger = logging.getLogger(__name__)

_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


async def _fetch_video_metadata(url: str) -> dict:
    """
    Fetch basic metadata from a TikTok video URL.

    Uses httpx to fetch the page and extract Open Graph meta tags —
    specifically og:description which contains the video caption
    and hashtags. No JavaScript rendering needed.

    Args:
        url: TikTok video URL e.g. https://www.tiktok.com/@user/video/123

    Returns:
        dict with url, description, hashtags
    """
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
        ) as client:
            resp = await client.get(url)
            html = resp.text

            # Extract og:description — contains video caption + hashtags
            desc_match = re.search(
                r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
                html
            )
            description = desc_match.group(1) if desc_match else ""

            # Extract hashtags from description
            hashtags = re.findall(r"#\w+", description)

            # Extract og:title as fallback
            title_match = re.search(
                r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
                html
            )
            title = title_match.group(1) if title_match else ""

            return {
                "url": url,
                "title": title,
                "description": description or title,
                "hashtags": hashtags,
            }

    except Exception as e:
        logger.warning(f"Failed to fetch metadata for {url}: {e}")
        return {
            "url": url,
            "title": "",
            "description": "",
            "hashtags": [],
        }


def _build_profiling_prompt(handle: str, videos: list[dict]) -> str:
    """
    Build the DNA profiling prompt for Claude.

    Formats all fetched video metadata into a structured prompt
    that asks Claude to identify the creator's content style,
    tone, hook patterns, and niche.
    """
    video_list = ""
    for i, v in enumerate(videos, 1):
        video_list += f"""
Video {i}:
  Description: {v['description']}
  Hashtags: {' '.join(v['hashtags']) if v['hashtags'] else 'none'}
"""

    return f"""You are a TikTok content analyst. Analyze these videos from creator @{handle} and build their content DNA profile.

CREATOR'S VIDEOS:
{video_list}

Based on these videos, extract the creator's content DNA. Respond in this exact JSON format:
{{
  "primary_niche": "the main content category e.g. beauty_skincare, fitness, fashion, home_kitchen, hair_care, wellness, cleaning, pets, tech_gadgets",
  "secondary_niches": ["other niches they cover"],
  "tone": "one of: casual_humor, educational, inspirational, authentic_raw, professional, entertaining",
  "hook_style": "one of: question_based, statement, story, reaction, tutorial, comparison",
  "avg_video_length": "estimated based on content complexity e.g. 15s, 30s, 60s",
  "audience_type": "describe their likely audience e.g. women_25_34, gen_z_teens, parents, fitness_enthusiasts",
  "content_style": "one of: talking_head, voiceover, text_only, demonstration, lifestyle",
  "posting_frequency": "estimated e.g. daily, 3x_week, weekly",
  "content_patterns": ["pattern 1", "pattern 2", "pattern 3"],
  "strong_topics": ["topic 1", "topic 2"],
  "avoid_topics": ["topic to avoid based on their style"]
}}

Respond with valid JSON only. No markdown, no extra text."""


async def build_creator_dna(
    handle: str,
    video_urls: list[str],
) -> CreatorDNA:
    """
    Build a DNA profile for a creator from their TikTok video URLs.

    Pipeline:
      1. Fetch metadata from each URL concurrently
      2. Build prompt with all video descriptions
      3. Send to Claude for style analysis
      4. Parse response into CreatorDNA object

    Args:
        handle    : creator's TikTok handle
        video_urls: list of 3-15 TikTok video URLs

    Returns:
        CreatorDNA with all fields populated
    """
    logger.info(f"Building DNA profile for @{handle} ({len(video_urls)} videos)")

    # 1. Fetch metadata from all URLs concurrently
    import asyncio
    tasks = [_fetch_video_metadata(url) for url in video_urls]
    videos = await asyncio.gather(*tasks)

    # Filter out videos where we got no description
    valid_videos = [v for v in videos if v["description"]]
    logger.info(f"  Got metadata for {len(valid_videos)}/{len(video_urls)} videos")

    # If we couldn't fetch any videos, use the URLs as context
    if not valid_videos:
        logger.warning(f"Could not fetch metadata — using URL list only")
        valid_videos = [{"url": u, "description": u, "hashtags": []} for u in video_urls]

    # 2. Build prompt
    prompt = _build_profiling_prompt(handle, valid_videos)

    # 3. Call Claude
    message = _client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]).strip()

    # 4. Parse response
    data = json.loads(raw)

    logger.info(
        f"DNA profile built for @{handle}: "
        f"niche={data.get('primary_niche')} "
        f"tone={data.get('tone')} "
        f"style={data.get('content_style')}"
    )

    return CreatorDNA(
        primary_niche=data.get("primary_niche", "general"),
        secondary_niches=data.get("secondary_niches", []),
        tone=data.get("tone", "casual_humor"),
        hook_style=data.get("hook_style", "statement"),
        avg_video_length=data.get("avg_video_length", "30s"),
        audience_type=data.get("audience_type", "general"),
        content_style=data.get("content_style", "talking_head"),
        posting_frequency=data.get("posting_frequency"),
        raw_dna=data,
    )
