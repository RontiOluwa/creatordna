# =============================================================================
# app/models.py — api-gateway
# =============================================================================
# Pydantic models with full request validation for the api-gateway.
# =============================================================================

from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
import re


# ── Request models ────────────────────────────────────────────────────────────

class CreatorOnboardRequest(BaseModel):
    """
    Payload for creator onboarding.
    Creator provides their TikTok handle and 3-15 video URLs.
    """
    tiktok_handle: str = Field(
        ...,
        description="TikTok handle with or without @ e.g. @username or username",
        min_length=2,
        max_length=50,
    )
    video_urls: list[str] = Field(
        ...,
        description="3-15 of their best performing TikTok video URLs",
        min_length=3,
        max_length=15,
    )
    email: Optional[str] = Field(
        None,
        description="Creator email address (optional)"
    )

    @field_validator("tiktok_handle")
    @classmethod
    def validate_handle(cls, v: str) -> str:
        # Strip @ and whitespace
        handle = v.lstrip("@").strip().lower()

        # Must not be empty after stripping
        if not handle:
            raise ValueError("TikTok handle cannot be empty")

        # Only allow alphanumeric, underscore, dot
        if not re.match(r"^[a-zA-Z0-9_.]{2,50}$", handle):
            raise ValueError(
                "TikTok handle can only contain letters, numbers, "
                "underscores and dots"
            )

        return handle

    @field_validator("video_urls")
    @classmethod
    def validate_urls(cls, urls: list[str]) -> list[str]:
        cleaned = []
        seen = set()

        for url in urls:
            url = url.strip()

            # Must be a valid URL format
            if not url.startswith("https://"):
                raise ValueError(
                    f"Invalid URL: '{url}' — must start with https://"
                )

            # Must be a TikTok URL
            if "tiktok.com" not in url:
                raise ValueError(
                    f"Invalid URL: '{url}' — must be a TikTok URL "
                    f"(tiktok.com)"
                )

            # No duplicates
            if url in seen:
                raise ValueError(f"Duplicate URL: '{url}'")
            seen.add(url)

            cleaned.append(url)

        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None

        v = v.strip().lower()

        # Basic email format check
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError(f"Invalid email format: '{v}'")

        return v


class FeedbackRequest(BaseModel):
    """
    Creator rates a delivered content idea.
    Feeds back into DNA profile refinement.
    """
    idea_id: int = Field(
        ...,
        description="ID of the content idea being rated",
        gt=0,   # must be positive
    )
    feedback: str = Field(
        ...,
        description="One of: made_it, not_my_style",
    )

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, v: str) -> str:
        allowed = {"made_it", "not_my_style"}
        if v not in allowed:
            raise ValueError(
                f"Invalid feedback '{v}' — must be one of: "
                f"{', '.join(sorted(allowed))}"
            )
        return v


# ── Response models ───────────────────────────────────────────────────────────

class CreatorDNA(BaseModel):
    """Claude-extracted DNA profile for a creator."""
    primary_niche: str
    secondary_niches: list[str] = []
    tone: str
    hook_style: str
    avg_video_length: str
    audience_type: str
    content_style: str
    posting_frequency: Optional[str] = None
    raw_dna: dict = {}


class OnboardResponse(BaseModel):
    """Response returned after successful creator onboarding."""
    creator_id: int
    tiktok_handle: str
    dna: CreatorDNA
    message: str = "Onboarding complete"
