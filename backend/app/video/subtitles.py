"""Geração de arquivos de legendas."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..transcription.base import TranscriptSegment


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(path: Path, segments: Iterable[TranscriptSegment], offset: float = 0.0) -> None:
    lines = []
    for idx, segment in enumerate(segments, start=1):
        start = format_timestamp(max(0.0, segment.start - offset))
        end = format_timestamp(max(0.0, segment.end - offset))
        text = segment.text.strip().replace("\n", " ")
        lines.append(f"{idx}\n{start} --> {end}\n{text}\n")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_vtt(path: Path, segments: Iterable[TranscriptSegment], offset: float = 0.0) -> None:
    lines = ["WEBVTT\n"]
    for segment in segments:
        start = format_timestamp(max(0.0, segment.start - offset)).replace(",", ".")
        end = format_timestamp(max(0.0, segment.end - offset)).replace(",", ".")
        text = segment.text.strip().replace("\n", " ")
        lines.append(f"{start} --> {end}\n{text}\n")
    path.write_text("\n".join(lines), encoding="utf-8")


__all__ = ["write_srt", "write_vtt", "format_timestamp"]
