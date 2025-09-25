"""Rotas de health-check."""
from __future__ import annotations

from fastapi import APIRouter

from ...observability.health import disk_usage, ffmpeg_version, redis_ok

router = APIRouter(tags=["Infra"])


@router.get("/health", summary="Health-check")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "ffmpeg_version": ffmpeg_version(),
        "redis_ok": redis_ok(),
        "disk": disk_usage("/"),
    }


__all__ = ["router"]
