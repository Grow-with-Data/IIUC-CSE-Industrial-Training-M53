"""API-key authentication for the versioned API surface."""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from fieldwork.core.config import settings

API_KEY_HEADER = "x-api-key"

# auto_error=False so a missing header raises our own 401 rather than FastAPI's
# bare 403, while still registering the scheme for the /docs "Authorize" button.
_api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


async def require_api_key(api_key: str | None = Depends(_api_key_header)) -> str:
    """Reject any request whose ``x-api-key`` header is missing or wrong."""
    expected = settings.PROJECT_API_KEY

    if not expected:
        # Fail closed: an unset key must not silently authorise everyone.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server is missing PROJECT_API_KEY configuration",
        )

    # compare_digest keeps the comparison constant-time; it needs a str on both
    # sides, so the missing-header case is normalised to "" first.
    if not secrets.compare_digest(api_key or "", expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or missing {API_KEY_HEADER} header",
        )

    return api_key
