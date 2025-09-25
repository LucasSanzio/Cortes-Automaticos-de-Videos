"""Processamento de cortes usando FFmpeg."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from ..config import get_settings
from ..observability.logging import get_logger
from ..observability.metrics import clips_generated_total, ffmpeg_failures_total
from ..transcription.base import TranscriptSegment
from .layout import build_scale_filter
from .subtitles import write_srt, write_vtt

logger = get_logger(__name__)


def _run_ffmpeg(command: List[str]) -> None:
    logger.info("executing_ffmpeg", command=" ".join(command))
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        ffmpeg_failures_total.inc()
        raise RuntimeError(f"FFmpeg falhou: {exc}") from exc


@dataclass
class CutResult:
    video_path: Path
    srt_path: Path
    vtt_path: Path
    thumbnail_path: Path


def cut_clip(
    source: Path,
    dest_dir: Path,
    start: float,
    end: float,
    segments: Iterable[TranscriptSegment],
    aspect_ratio: str,
    burn_subtitles: bool,
) -> CutResult:
    settings = get_settings()
    dest_dir.mkdir(parents=True, exist_ok=True)
    video_path = dest_dir / "clip.mp4"
    srt_path = dest_dir / "clip.srt"
    vtt_path = dest_dir / "clip.vtt"
    thumb_path = dest_dir / "thumb.jpg"

    write_srt(srt_path, segments, offset=start)
    write_vtt(vtt_path, segments, offset=start)

    layout = build_scale_filter(1280, 720, aspect_ratio)
    base_filters = layout.filters
    vf_filter = base_filters
    if burn_subtitles:
        vf_filter = f"{base_filters},subtitles={srt_path}"

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start}",
        "-to",
        f"{end}",
        "-i",
        str(source),
    ]
    if settings.fast_cut:
        command += ["-c", "copy"]
    else:
        command += [
            "-vf",
            vf_filter,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
        ]
    command.append(str(video_path))
    _run_ffmpeg(command)

    mid = start + (end - start) / 2
    thumb_cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{mid}",
        "-i",
        str(source),
        "-vframes",
        "1",
        str(thumb_path),
    ]
    _run_ffmpeg(thumb_cmd)

    clips_generated_total.inc()
    return CutResult(video_path=video_path, srt_path=srt_path, vtt_path=vtt_path, thumbnail_path=thumb_path)


__all__ = ["cut_clip", "CutResult"]
