# =============================================================================
# app/routes/auth.py — api-gateway
# =============================================================================
# Authentication endpoints.
#
# Routes:
#   POST /auth/register — create a new creator account
#   POST /auth/login    — login and get JWT token
#   GET  /auth/me       — get current creator from token
# =============================================================================

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from app.auth import (
    hash_password, verify_password,
    create_access_token, get_current_creator
)
from shared.database import get_conn, release_conn
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Request models ────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    tiktok_handle: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., description="Creator email address")
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("tiktok_handle")
    @classmethod
    def validate_handle(cls, v: str) -> str:
        handle = v.lstrip("@").strip().lower()
        if not handle:
            raise ValueError("Handle cannot be empty")
        if not re.match(r"^[a-zA-Z0-9_.]{2,50}$", handle):
            raise ValueError(
                "Handle can only contain letters, numbers, underscores and dots"
            )
        return handle

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v
        ):
            raise ValueError(f"Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 72:
            raise ValueError("Password must be 72 characters or fewer")
        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register")
async def register(request: RegisterRequest):
    """
    Register a new creator account.

    Creates the creator record with hashed password.
    Does NOT run DNA profiling — that happens separately
    via POST /creators/onboard after registration.

    Returns JWT token so creator is immediately logged in.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()

        # Check handle not taken
        cur.execute(
            "SELECT id FROM creators WHERE tiktok_handle = %s",
            (request.tiktok_handle,)
        )
        if cur.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"Handle @{request.tiktok_handle} is already registered"
            )

        # Check email not taken
        cur.execute(
            "SELECT id FROM creators WHERE email = %s",
            (request.email,)
        )
        if cur.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Email is already registered"
            )

        # Insert creator with hashed password
        cur.execute("""
            INSERT INTO creators (tiktok_handle, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (
            request.tiktok_handle,
            request.email,
            hash_password(request.password),
        ))
        creator_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        logger.info(
            f"Creator registered: @{request.tiktok_handle} "
            f"(id={creator_id})"
        )

        # Return token — creator is immediately logged in
        token = create_access_token(creator_id, request.tiktok_handle)
        return {
            "access_token": token,
            "token_type": "bearer",
            "creator_id": creator_id,
            "tiktok_handle": request.tiktok_handle,
            "message": "Registration successful — now call POST /creators/onboard to complete setup",
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        release_conn(conn)


@router.post("/login")
async def login(request: LoginRequest):
    """
    Login with email and password.
    Returns a JWT token valid for JWT_EXPIRY_HOURS hours.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, tiktok_handle, password_hash, is_active
            FROM creators
            WHERE email = %s
        """, (request.email.strip().lower(),))
        row = cur.fetchone()
        cur.close()

        # Same error for both wrong email and wrong password
        # — prevents user enumeration
        if not row:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        creator_id, handle, password_hash, is_active = row

        if not password_hash:
            raise HTTPException(
                status_code=401,
                detail="This account was created without a password — use onboard flow"
            )

        if not verify_password(request.password, password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not is_active:
            raise HTTPException(
                status_code=403,
                detail="Account is deactivated"
            )

        token = create_access_token(creator_id, handle)
        logger.info(f"Creator logged in: @{handle} (id={creator_id})")

        return {
            "access_token": token,
            "token_type": "bearer",
            "creator_id": creator_id,
            "tiktok_handle": handle,
        }

    finally:
        release_conn(conn)


@router.get("/me")
async def get_me(creator: dict = Depends(get_current_creator)):
    """
    Get the currently authenticated creator.
    Requires Bearer token in Authorization header.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, tiktok_handle, email, is_active, created_at
            FROM creators
            WHERE id = %s
        """, (int(creator["sub"]),))
        row = cur.fetchone()
        cur.close()

        if not row:
            raise HTTPException(status_code=404, detail="Creator not found")

        return {
            "id": row[0],
            "tiktok_handle": row[1],
            "email": row[2],
            "is_active": row[3],
            "created_at": str(row[4]),
        }
    finally:
        release_conn(conn)
