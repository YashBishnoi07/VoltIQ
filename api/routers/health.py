"""Health check router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "VoltIQ API",
        "version": "0.1.0",
    }
