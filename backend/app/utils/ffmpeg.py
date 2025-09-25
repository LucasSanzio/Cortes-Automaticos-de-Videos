"""Helpers relacionados ao FFmpeg."""
from __future__ import annotations

import subprocess
from pathlib import Path


def extract_audio(source: Path, dest: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(dest),
    ]
    subprocess.run(command, check=True)


__all__ = ["extract_audio"]
