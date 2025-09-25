"""Utilidades para inspecionar mídia com ffprobe."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MediaInfo:
    duration: float
    width: int
    height: int
    codec: str


def probe_media(path: Path) -> MediaInfo:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    duration = float(data.get("format", {}).get("duration", 0.0))
    stream: dict[str, Any] = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
        {},
    )
    width = int(stream.get("width", 0))
    height = int(stream.get("height", 0))
    codec = str(stream.get("codec_name", ""))
    return MediaInfo(duration=duration, width=width, height=height, codec=codec)


__all__ = ["MediaInfo", "probe_media"]
