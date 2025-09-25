"""Modelos ORM utilizados pela aplicação."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, List, Optional
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    TRANSCRIBING = "TRANSCRIBING"
    ANALYZING = "ANALYZING"
    CUTTING = "CUTTING"
    DONE = "DONE"
    ERROR = "ERROR"


class SourceType(str, enum.Enum):
    UPLOAD = "UPLOAD"
    URL = "URL"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    status: Mapped[str] = mapped_column(Enum(JobStatus), default=JobStatus.QUEUED)
    source_type: Mapped[str] = mapped_column(Enum(SourceType))
    source_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transcript_json_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    analysis_json_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    webhook_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    partial: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clips: Mapped[List["Clip"]] = relationship("Clip", back_populates="job", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status.value if isinstance(self.status, JobStatus) else self.status,
            "source_type": self.source_type.value if isinstance(self.source_type, SourceType) else self.source_type,
            "source_path": self.source_path,
            "source_url": self.source_url,
            "checksum": self.checksum,
            "duration_seconds": self.duration_seconds,
            "transcript_json_path": self.transcript_json_path,
            "analysis_json_path": self.analysis_json_path,
            "webhook_url": self.webhook_url,
            "partial": self.partial,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"))
    start_sec: Mapped[float] = mapped_column(Float)
    end_sec: Mapped[float] = mapped_column(Float)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[Optional[str]] = mapped_column(String(240), nullable=True)
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(240), nullable=True)
    video_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    srt_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    vtt_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    aspect_ratio: Mapped[str] = mapped_column(String(8), default="16:9")

    job: Mapped[Job] = relationship("Job", back_populates="clips")

    def to_dict(self, public_base_url: Optional[str] = None) -> dict[str, Any]:
        def _make_url(path: Optional[str]) -> Optional[str]:
            if not path:
                return None
            if public_base_url and not path.startswith("http"):
                return f"{public_base_url.rstrip('/')}/{path.lstrip('/')}"
            return path

        return {
            "id": self.id,
            "start_sec": self.start_sec,
            "end_sec": self.end_sec,
            "title": self.title,
            "description": self.description,
            "tags": self.tags or [],
            "confidence": self.confidence,
            "reason": self.reason,
            "aspect_ratio": self.aspect_ratio,
            "video_url": _make_url(self.video_path),
            "srt_url": _make_url(self.srt_path),
            "vtt_url": _make_url(self.vtt_path),
            "thumbnail_url": _make_url(self.thumbnail_path),
        }


__all__ = ["Job", "Clip", "JobStatus", "SourceType"]
