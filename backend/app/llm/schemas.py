"""Esquemas utilizados pela seleção de destaques."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, validator


class HighlightClip(BaseModel):
    start_sec: float = Field(..., ge=0)
    end_sec: float = Field(..., gt=0)
    title: str = Field(..., max_length=80)
    description: str = Field("", max_length=160)
    tags: List[str] = Field(default_factory=list)
    confidence: float = Field(0.5, ge=0, le=1)
    reason: str = Field("", max_length=160)

    @validator("end_sec")
    def validate_order(cls, value: float, values: dict[str, float]):  # noqa: D401
        """Garante que o fim seja maior que o início."""

        start = values.get("start_sec", 0)
        if value <= start:
            raise ValueError("end_sec deve ser maior que start_sec")
        return value


class HighlightPlan(BaseModel):
    clips: List[HighlightClip] = Field(default_factory=list)

    def clamp(self, duration: float, min_length: float, max_length: float, max_clips: int) -> "HighlightPlan":
        """Ajusta os clipes aos limites configurados."""

        filtered: List[HighlightClip] = []
        for clip in self.clips:
            start = max(0.0, min(duration, clip.start_sec))
            end = max(0.0, min(duration, clip.end_sec))
            if end <= start:
                continue
            length = end - start
            if length < min_length or length > max_length:
                continue
            filtered.append(clip.copy(update={"start_sec": start, "end_sec": end}))
        filtered = sorted(filtered, key=lambda c: c.start_sec)
        result: List[HighlightClip] = []
        last_end = -1.0
        for clip in filtered:
            if clip.start_sec < last_end:
                continue
            result.append(clip)
            last_end = clip.end_sec
            if len(result) >= max_clips:
                break
        return HighlightPlan(clips=result)


__all__ = ["HighlightClip", "HighlightPlan"]
