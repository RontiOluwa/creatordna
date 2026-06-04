# =============================================================================
# app/scraper.py
# =============================================================================
# Kalodata API client for the ingestion service.
#
# Responsibilities:
#   - Fetch top 10 videos per keyword search from Kalodata (free tier limit)
#   - Normalise raw API response into RawVideo objects
#   - Insert into raw_videos table with deduplication
#   - Return ScrapeResult summary for logging and monitoring
#
# Free tier limits:
#   - 10 searches per day total
#   - Page 1 only (pagination locked behind paid plan)
#   - 10 results per page
#
# Why keywords instead of category IDs?
#   Kalodata's free tier returns the same top viral videos regardless of
#   category filter. Searching by niche-specific keywords returns genuinely
#   different videos per niche, giving us diverse training data.
# =============================================================================

import requests
import json
import logging
import time
from typing import Optional
from app.config import settings
from app.models import RawVideo, ScrapeResult
from app.database import get_conn, release_conn

logger = logging.getLogger(__name__)

# Keyword search terms per niche.
# Each entry uses 1 of the 10 daily free tier searches.
# Keywords are chosen to surface high-GMV affiliate content in each niche.
KEYWORDS = {
    "beauty_skincare":  "skincare serum moisturizer",
    "hair_care":        "wig lace frontal hair extensions",
    "fitness":          "workout gym resistance bands",
    "home_kitchen":     "kitchen gadget air fryer cooking",
    "fashion":          "outfit aesthetic fashion haul",
    "wellness":         "supplement vitamins health",
    "cleaning":         "cleaning mop vacuum",
    "pets":             "dog cat pet supplies",
    "tech_gadgets":     "gadget phone accessories",
}

KALODATA_URL = "https://www.kalodata.com/video/queryList"
KALODATA_SEARCH_URL = "https://www.kalodata.com/video/searchList"


def _build_headers() -> dict:
    """
    Build request headers for Kalodata API.
    Cookie is loaded from environment — refresh when it expires.
    Accept-Encoding is intentionally omitted so requests handles
    decompression automatically.
    """
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Cookie": settings.KALODATA_COOKIE,
        "Country": "US",
        "Currency": "USD",
        "Language": "en-US",
        "Origin": "https://www.kalodata.com",
        "Referer": "https://www.kalodata.com/video",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        ),
    }


def _parse_revenue(rev_str: Optional[str]) -> Optional[float]:
    """
    Parse formatted revenue string to float.
    "$65.83k" -> 65830.0
    "$1.11m"  -> 1110000.0
    """
    if not rev_str:
        return None
    s = rev_str.replace("$", "").replace(",", "").strip().lower()
    try:
        if s.endswith("m"):
            return float(s[:-1]) * 1_000_000
        elif s.endswith("k"):
            return float(s[:-1]) * 1_000
        return float(s)
    except ValueError:
        return None


def _parse_views(v) -> Optional[int]:
    """
    Parse views to integer.
    "23.36m" -> 23360000
    "5.7m"   -> 5700000
    """
    if not v:
        return None
    s = str(v).replace(",", "").strip().lower()
    try:
        if s.endswith("m"):
            return int(float(s[:-1]) * 1_000_000)
        elif s.endswith("k"):
            return int(float(s[:-1]) * 1_000)
        return int(float(s))
    except ValueError:
        return None


def _fetch_by_keyword(keyword: str, niche_name: str) -> list[dict]:
    """
    Search Kalodata by keyword instead of category ID.

    Returns genuinely different videos per niche on the free tier.
    Category ID filtering returns the same top viral videos regardless
    of which category is selected — keyword search avoids this.

    Args:
        keyword   : search term e.g. "skincare serum moisturizer"
        niche_name: human label used only for logging

    Returns:
        list of raw video dicts from Kalodata API
    """
    payload = {
        "country": "US",
        "startDate": settings.SCRAPE_START_DATE,
        "endDate": settings.SCRAPE_END_DATE,
        "cateIds": [],
        "showCateIds": [],
        "pageNo": 1,
        "pageSize": 10,
        "sort": [{"field": "revenue", "type": "DESC"}],
        "video.filter.video_type": "WithProduct",
        "video.filter.ad.daily_roas": "",
        "title": keyword,   # "title" is the correct field name for search
    }

    logger.debug(f"Fetching keyword='{keyword}' for niche='{niche_name}'")

    resp = requests.post(
        KALODATA_SEARCH_URL,
        headers=_build_headers(),
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        raise Exception(f"Kalodata error: {data.get('message', 'unknown')}")

    items = data.get("data", [])
    logger.info(f"  Received {len(items)} items for '{niche_name}'")
    return items


def _normalise(item: dict, niche: str, keyword: str) -> RawVideo:
    """
    Convert a raw Kalodata API item into a normalised RawVideo object.

    Args:
        item    : raw dict from Kalodata API response
        niche   : category name e.g. "beauty_skincare"
        keyword : search keyword used to find this video
    """
    revenue_str = item.get("revenue", "")
    return RawVideo(
        tiktok_video_id=str(item.get("id") or item.get("videoId") or ""),
        handle=item.get("handle"),
        description=item.get("description"),
        duration=item.get("duration"),
        revenue=revenue_str,
        revenue_raw=_parse_revenue(revenue_str),
        items_sold=item.get("sale"),
        views=_parse_views(item.get("views")),
        gpm=item.get("gpm"),
        ad_cpa=item.get("ad_cpa"),
        ad_view_ratio=item.get("ad_view_ratio"),
        ad_roas=item.get("ad_roas") or item.get("adRoas"),
        niche=niche,
        category_id=keyword,   # storing keyword in category_id for reference
        revenue_trend=item.get("revenue_trend", []),
        views_trend=item.get("views_trend", []),
        raw_json=item,
    )


def _insert_video(video: RawVideo) -> bool:
    """
    Insert a RawVideo into the raw_videos table.
    Returns True if inserted, False if duplicate (already exists).

    Uses ON CONFLICT DO NOTHING on tiktok_video_id to safely
    skip videos we have already seen without raising an error.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO raw_videos (
                tiktok_video_id, handle, description, duration,
                revenue, revenue_raw, items_sold, views,
                gpm, ad_cpa, ad_view_ratio, ad_roas,
                niche, category_id, revenue_trend, views_trend, raw_json
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )
            ON CONFLICT (tiktok_video_id) DO NOTHING
        """, (
            video.tiktok_video_id,
            video.handle,
            video.description,
            video.duration,
            video.revenue,
            video.revenue_raw,
            video.items_sold,
            video.views,
            video.gpm,
            video.ad_cpa,
            video.ad_view_ratio,
            video.ad_roas,
            video.niche,
            video.category_id,
            json.dumps(video.revenue_trend),
            json.dumps(video.views_trend),
            json.dumps(video.raw_json),
        ))
        inserted = cur.rowcount > 0
        conn.commit()
        cur.close()
        return inserted
    except Exception as e:
        conn.rollback()
        logger.error(f"Insert failed for {video.tiktok_video_id}: {e}")
        return False
    finally:
        release_conn(conn)


def scrape_category(category_name: str, keyword: str) -> ScrapeResult:
    """
    Full scrape pipeline for one niche:
      1. Fetch from Kalodata using keyword search
      2. Normalise each item into a RawVideo
      3. Insert into DB (skip duplicates)
      4. Return ScrapeResult summary

    Args:
        category_name : niche label e.g. "beauty_skincare"
        keyword       : search term e.g. "skincare serum moisturizer"
    """
    logger.info(f"Scraping: {category_name} (keyword='{keyword}')")

    try:
        items = _fetch_by_keyword(keyword, category_name)
        found = len(items)
        new = 0

        for item in items:
            video = _normalise(item, category_name, keyword)
            if video.tiktok_video_id and _insert_video(video):
                new += 1

        logger.info(f"  {category_name}: {found} found, {new} new")
        return ScrapeResult(
            category=category_name,
            videos_found=found,
            videos_new=new,
            status="success",
        )

    except Exception as e:
        logger.error(f"  {category_name}: failed — {e}")
        return ScrapeResult(
            category=category_name,
            status="error",
            error_message=str(e),
        )


def run_full_scrape() -> list[ScrapeResult]:
    """
    Run scrape across all configured keyword searches.
    Called by the scheduler daily and by POST /ingest/trigger manually.

    Iterates over KEYWORDS dict — one search per niche.
    Sleeps between requests to avoid hammering Kalodata.
    Stops early if the daily search limit is hit.

    Returns:
        list of ScrapeResult — one per niche attempted
    """
    # Guard: abort early if cookie is missing
    if not settings.KALODATA_COOKIE:
        logger.error("KALODATA_COOKIE is not set — scrape aborted")
        return []

    logger.info(f"Starting full scrape — {len(KEYWORDS)} niches")
    results = []

    for name, keyword in KEYWORDS.items():
        result = scrape_category(name, keyword)
        results.append(result)

        # Stop if daily search limit reached
        if (
            result.status == "error"
            and result.error_message
            and "used up" in result.error_message
        ):
            logger.warning(
                "Daily search limit reached — stopping scrape early")
            break

        # Polite delay between requests
        time.sleep(settings.SCRAPE_DELAY_SECONDS)

    total_new = sum(r.videos_new for r in results)
    total_found = sum(r.videos_found for r in results)
    logger.info(
        f"Scrape complete — {total_new} new videos, "
        f"{total_found} total found across {len(results)} niches"
    )
    return results
