"""Conversões de tempo."""
from __future__ import annotations


def to_seconds(timecode: str) -> float:
    parts = timecode.split(":")
    if len(parts) != 3:
        raise ValueError("Timecode deve estar no formato HH:MM:SS.mmm")
    hours, minutes, seconds = parts
    sec = float(seconds)
    return int(hours) * 3600 + int(minutes) * 60 + sec


def to_timecode(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{sec:06.3f}"


__all__ = ["to_seconds", "to_timecode"]
