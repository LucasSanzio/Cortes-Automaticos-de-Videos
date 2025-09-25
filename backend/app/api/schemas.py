"""Schemas Pydantic para a API."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from ..db.models import JobStatus


class ClipResponse(BaseModel):
    id: str
    start_sec: float
    end_sec: float
    title: str
    description: Optional[str]
    tags: List[str]
    confidence: Optional[float]
    reason: Optional[str]
    aspect_ratio: str
    video_url: Optional[str]
    srt_url: Optional[str]
    vtt_url: Optional[str]
    thumbnail_url: Optional[str]


class JobParams(BaseModel):
    max_clips: int = Field(default=5, ge=1, le=10)
    min_clip_sec: int = Field(default=20, ge=5)
    max_clip_sec: int = Field(default=90, ge=10)
    target_aspect: str = Field(default="16:9")
    burn_subtitles: bool = Field(default=True)
    language: str = Field(default="pt")
    llm_style: str = Field(default="default")


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    params: JobParams


class JobDetailResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: float = Field(ge=0, le=100)
    step: Optional[str]
    error_message: Optional[str]
    clips: List[ClipResponse] = Field(default_factory=list)
    params: JobParams


class JobCreateRequest(BaseModel):
    source_url: Optional[HttpUrl] = None
    max_clips: Optional[int] = Field(default=None, ge=1, le=10)
    min_clip_sec: Optional[int] = Field(default=None, ge=5)
    max_clip_sec: Optional[int] = Field(default=None, ge=10)
    target_aspect: Optional[str] = None
    burn_subtitles: Optional[bool] = None
    language: Optional[str] = None
    llm_style: Optional[str] = None
    webhook_url: Optional[HttpUrl] = None
    reuse_existing: Optional[bool] = Field(default=False)


class RecutRequest(BaseModel):
    max_clips: Optional[int] = Field(default=None, ge=1, le=10)
    min_clip_sec: Optional[int] = Field(default=None, ge=5)
    max_clip_sec: Optional[int] = Field(default=None, ge=10)
    llm_style: Optional[str] = None


__all__ = [
    "ClipResponse",
    "JobParams",
    "JobCreateResponse",
    "JobDetailResponse",
    "JobCreateRequest",
    "RecutRequest",
]
