"""Funções utilitárias de health-check."""
from __future__ import annotations

import shutil
import subprocess
from typing import Any

from redis import Redis

from ..config import get_settings


def ffmpeg_version() -> str:
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)
        return result.stdout.splitlines()[0]
    except Exception:  # pragma: no cover
        return "indisponível"


def redis_ok() -> bool:
    settings = get_settings()
    try:
        client = Redis.from_url(settings.redis_url)
        client.ping()
        return True
    except Exception:  # pragma: no cover - ambiente de teste sem redis real
        return False


def disk_usage(path: str) -> dict[str, Any]:
    usage = shutil.disk_usage(path)
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
    }


__all__ = ["ffmpeg_version", "redis_ok", "disk_usage"]
