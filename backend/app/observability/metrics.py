"""Integração com Prometheus."""
from __future__ import annotations

from prometheus_client import Counter, Histogram

jobs_total = Counter("jobs_total", "Total de jobs processados", ["status"])
clips_generated_total = Counter("clips_generated_total", "Total de clipes gerados")
llm_calls_total = Counter("llm_calls_total", "Chamadas ao LLM", ["provider", "status"])
whisper_duration_seconds = Histogram("whisper_duration_seconds", "Duração do processamento de áudio")
job_duration_seconds = Histogram("job_duration_seconds", "Tempo total por job")
ffmpeg_failures_total = Counter("ffmpeg_failures_total", "Falhas no FFmpeg")

__all__ = [
    "jobs_total",
    "clips_generated_total",
    "llm_calls_total",
    "whisper_duration_seconds",
    "job_duration_seconds",
    "ffmpeg_failures_total",
]
