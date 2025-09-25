"""Gerenciamento de progresso via Redis."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from redis import Redis
from typing import Any, cast

@dataclass
class JobProgress:
    status: str
    step: str
    progress: float


def progress_key(job_id: str) -> str:
    return f"job:{job_id}:progress"


def set_progress(redis: Redis, job_id: str, status: str, step: str, progress: float) -> None:
    data = JobProgress(status=status, step=step, progress=progress)
    redis.set(progress_key(job_id), json.dumps(data.__dict__), ex=60 * 60 * 6)


def get_progress(redis: Redis, job_id: str) -> Optional[JobProgress]:
    value = cast(Any, redis.get(progress_key(job_id)))
    if not value:
        return None
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    data = json.loads(value)
    return JobProgress(**data)


__all__ = ["set_progress", "get_progress", "JobProgress"]
