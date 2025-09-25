"""Tarefas executadas pelos workers."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterable, List

from redis import Redis

from ..config import get_settings
from ..db.base import SessionLocal, init_db
from ..db.models import Clip, Job, JobStatus
from ..db.repo import ClipRepo, JobRepo
from ..llm.highlight_selector import HighlightSelector, HighlightSelectorParams
from ..observability.logging import get_logger
from ..observability.metrics import job_duration_seconds, jobs_total, whisper_duration_seconds
from ..transcription.base import TranscriptSegment
from ..transcription.whisper_local import LocalWhisperProvider
from ..video.cutter import cut_clip
from ..video.probe import probe_media
from .progress import set_progress

logger = get_logger(__name__)
_settings = get_settings()


def get_redis() -> Redis:
    return Redis.from_url(_settings.redis_url)


def _job_dir(job: Job) -> Path:
    return Path(_settings.data_dir) / "jobs" / job.id


def process_job(job_id: str) -> None:
    init_db()
    redis = get_redis()
    start_time = time.time()
    with SessionLocal() as session:
        job_repo = JobRepo(session)
        clip_repo = ClipRepo(session)
        job = job_repo.get(job_id)
        if not job:
            logger.error("job_not_found", job_id=job_id)
            return
        try:
            _run_pipeline(redis, job_repo, clip_repo, job)
            jobs_total.labels(status="success").inc()
        except Exception as exc:
            job.status = JobStatus.ERROR
            job.error_message = str(exc)
            jobs_total.labels(status="error").inc()
            logger.error("job_failed", job_id=job_id, error=str(exc))
        finally:
            session.commit()
            duration = time.time() - start_time
            job_duration_seconds.observe(duration)


def _run_pipeline(redis: Redis, job_repo: JobRepo, clip_repo: ClipRepo, job: Job) -> None:
    set_progress(redis, job.id, JobStatus.TRANSCRIBING.value, "TRANSCRIBING", 5)
    job.status = JobStatus.TRANSCRIBING

    media_path = Path(job.source_path or "")
    if not media_path.exists():
        raise FileNotFoundError("Arquivo de origem não encontrado")

    media_info = probe_media(media_path)
    job.duration_seconds = media_info.duration

    whisper = LocalWhisperProvider(_settings.whisper_model)
    t0 = time.time()
    transcript = whisper.transcribe(media_path, _settings.language)
    whisper_duration_seconds.observe(time.time() - t0)
    transcript_path = _job_dir(job) / "transcript.json"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(json.dumps([seg.__dict__ for seg in transcript.segments]))
    job.transcript_json_path = str(transcript_path.relative_to(_settings.data_dir))

    set_progress(redis, job.id, JobStatus.ANALYZING.value, "ANALYZING", 35)
    job.status = JobStatus.ANALYZING

    selector = HighlightSelector()
    params = HighlightSelectorParams(
        max_clips=_settings.llm_max_clips,
        min_clip_sec=_settings.min_clip_sec,
        max_clip_sec=_settings.max_clip_sec,
        llm_style="default",
        language=_settings.language,
    )
    transcript_texts = [segment.text for segment in transcript.segments]
    plan = selector.select(transcript_texts, transcript.duration, params)
    analysis_path = _job_dir(job) / "analysis.json"
    analysis_path.write_text(plan.model_dump_json())
    job.analysis_json_path = str(analysis_path.relative_to(_settings.data_dir))

    set_progress(redis, job.id, JobStatus.CUTTING.value, "CUTTING", 60)
    job.status = JobStatus.CUTTING

    for idx, clip in enumerate(plan.clips, start=1):
        dest = _job_dir(job) / f"clip_{idx:02d}"
        segments = _filter_segments(transcript.segments, clip.start_sec, clip.end_sec)
        result = cut_clip(
            media_path,
            dest,
            clip.start_sec,
            clip.end_sec,
            segments,
            _settings.target_aspect,
            _settings.burn_subtitles,
        )
        clip_record = Clip(
            job_id=job.id,
            start_sec=clip.start_sec,
            end_sec=clip.end_sec,
            title=clip.title,
            description=clip.description,
            tags=clip.tags,
            confidence=clip.confidence,
            reason=clip.reason,
            video_path=str(result.video_path.relative_to(_settings.data_dir)),
            srt_path=str(result.srt_path.relative_to(_settings.data_dir)),
            vtt_path=str(result.vtt_path.relative_to(_settings.data_dir)),
            thumbnail_path=str(result.thumbnail_path.relative_to(_settings.data_dir)),
            aspect_ratio=_settings.target_aspect,
        )
        clip_repo.create(clip_record)

    set_progress(redis, job.id, JobStatus.DONE.value, "DONE", 100)
    job.status = JobStatus.DONE


def _filter_segments(segments: Iterable[TranscriptSegment], start: float, end: float) -> List[TranscriptSegment]:
    return [segment for segment in segments if segment.end > start and segment.start < end]


__all__ = ["process_job", "get_redis"]
