# =============================================================================
# app/auth.py — delivery-service
# =============================================================================
# Internal service authentication.
# Verifies requests come from the api-gateway via shared secret header.
#
# The api-gateway attaches X-Internal-Secret on every proxied request.
# Direct calls to the delivery service without this header are rejected.
# =============================================================================

import os
from fastapi import Header, HTTPException

INTERNAL_SECRET = os.getenv("INTERNAL_SERVICE_SECRET", "")


def verify_internal(x_internal_secret: str = Header(...)):
    """
    FastAPI dependency — verifies the internal service secret.

    Usage:
        @router.post("/deliver/{handle}")
        async def route(_: None = Depends(verify_internal)):
            ...

    Raises:
        HTTPException 403 if secret is missing or wrong
        HTTPException 500 if secret not configured on server
    """
    if not INTERNAL_SECRET:
        raise HTTPException(
            status_code=500,
            detail="INTERNAL_SERVICE_SECRET not configured"
        )
    if x_internal_secret != INTERNAL_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Forbidden — invalid internal secret"
        )
