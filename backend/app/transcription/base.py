"""Interfaces de transcrição."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Protocol


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    duration: float
    segments: List[TranscriptSegment]


class TranscriptionProvider(Protocol):
    def transcribe(self, media_path: Path, language: str) -> TranscriptResult:
        ...


__all__ = ["TranscriptSegment", "TranscriptResult", "TranscriptionProvider"]
