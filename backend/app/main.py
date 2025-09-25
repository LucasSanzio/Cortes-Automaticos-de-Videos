"""Aplicação FastAPI principal."""

from pathlib import Path
from typing import Optional

from fastapi import Body, Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .api.errors import INVALID_FILE, NOT_FOUND
from .api.routers import health
from .api.schemas import (
    ClipResponse,
    JobCreateRequest,
    JobCreateResponse,
    JobDetailResponse,
    JobParams,
    RecutRequest,
)
from .config import get_settings
from .db.base import init_db
from .db.models import Job, JobStatus, SourceType
from .db.repo import ClipRepo, JobRepo
from .deps import get_db
from .observability.logging import configure_logging, get_logger
from .security import require_api_key
from .utils.hash import file_checksum
from .utils.io import allowed_extension
from .workers.queue import enqueue_job
from .workers.progress import get_progress

settings = get_settings()
configure_logging(settings.log_level)
app = FastAPI(title="Cortes Automáticos", version="1.0.0")
rate_limit = settings.rate_limit
if rate_limit.endswith('/min'):
    rate_limit = rate_limit[:-4] + '/minute'
limiter = Limiter(key_func=get_remote_address, default_limits=[rate_limit])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

Instrumentator().instrument(app).expose(app, include_in_schema=False)
app.include_router(health.router)

logger = get_logger(__name__)


@app.on_event("startup")
async def startup_event() -> None:  # pragma: no cover - apenas inicialização
    init_db()


@app.post(
    "/jobs",
    response_model=JobCreateResponse,
    summary="Cria um novo job a partir de upload ou URL",
)
@limiter.limit(settings.rate_limit)
async def create_job(
    request: Request,
    db=Depends(get_db),
    api_key: str = Depends(require_api_key),
    file: Optional[UploadFile] = File(default=None),
    max_clips: int = Form(default=settings.llm_max_clips),
    min_clip_sec: int = Form(default=settings.min_clip_sec),
    max_clip_sec: int = Form(default=settings.max_clip_sec),
    target_aspect: str = Form(default=settings.target_aspect),
    burn_subtitles: bool = Form(default=settings.burn_subtitles),
    language: str = Form(default=settings.language),
    llm_style: str = Form(default="default"),
    webhook_url: str | None = Form(default=None),
    reuse_existing: bool = Form(default=False),
    body: JobCreateRequest | None = Body(default=None),
):
    job_repo = JobRepo(db)

    # JSON request (sem arquivo)
    if not file and body:
        if not body.source_url:
            raise INVALID_FILE
        job = Job(
            source_type=SourceType.URL,
            source_url=str(body.source_url),
            status=JobStatus.ERROR,
            error_message="Ingestão via URL não habilitada neste ambiente",
        )
        job_repo.create(job)
        db.commit()
        status_enum = job.status if isinstance(job.status, JobStatus) else JobStatus(job.status)
        return JobCreateResponse(
            job_id=job.id,
            status=status_enum,
            created_at=job.created_at,
            params=JobParams(
                max_clips=body.max_clips or settings.llm_max_clips,
                min_clip_sec=body.min_clip_sec or settings.min_clip_sec,
                max_clip_sec=body.max_clip_sec or settings.max_clip_sec,
                target_aspect=body.target_aspect or settings.target_aspect,
                burn_subtitles=body.burn_subtitles if body.burn_subtitles is not None else settings.burn_subtitles,
                language=body.language or settings.language,
                llm_style=body.llm_style or "default",
            ),
        )

    if not file:
        raise INVALID_FILE

    if not allowed_extension(file.filename or "", settings.allowed_ext.split(",")):
        raise INVALID_FILE

    job = Job(
        source_type=SourceType.UPLOAD,
        status=JobStatus.QUEUED,
    )
    job_repo.create(job)

    dest_dir = Path(settings.data_dir) / "jobs" / job.id
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(file.filename or "upload.mp4").name
    dest_path = dest_dir / filename
    with dest_path.open("wb") as buffer:
        buffer.write(await file.read())
    job.source_path = str(dest_path)
    job.checksum = file_checksum(dest_path)
    job.webhook_url = webhook_url
    db.commit()

    enqueue_job(job.id)

    status_enum = job.status if isinstance(job.status, JobStatus) else JobStatus(job.status)
    return JobCreateResponse(
        job_id=job.id,
        status=status_enum,
        created_at=job.created_at,
        params=JobParams(
            max_clips=max_clips,
            min_clip_sec=min_clip_sec,
            max_clip_sec=max_clip_sec,
            target_aspect=target_aspect,
            burn_subtitles=burn_subtitles,
            language=language,
            llm_style=llm_style,
        ),
    )


@app.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job(job_id: str, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    job_repo = JobRepo(db)
    job = job_repo.get(job_id)
    if not job:
        raise NOT_FOUND
    clip_repo = ClipRepo(db)
    base_url = str(settings.public_base_url) if settings.public_base_url else None
    raw_clips = [clip.to_dict(base_url) for clip in clip_repo.list_by_job(job_id)]
    clips = [ClipResponse.model_validate(item) for item in raw_clips]
    try:
        from .workers.tasks import get_redis

        redis = get_redis()
        progress = get_progress(redis, job_id)
    except Exception:
        progress = None
    status = job.status if isinstance(job.status, JobStatus) else JobStatus(job.status)
    return JobDetailResponse(
        job_id=job.id,
        status=status,
        progress=progress.progress if progress else (100.0 if status == JobStatus.DONE else 0.0),
        step=progress.step if progress else status.value,
        error_message=job.error_message,
        clips=clips,
        params=JobParams(
            max_clips=settings.llm_max_clips,
            min_clip_sec=settings.min_clip_sec,
            max_clip_sec=settings.max_clip_sec,
            target_aspect=settings.target_aspect,
            burn_subtitles=settings.burn_subtitles,
            language=settings.language,
            llm_style="default",
        ),
    )


@app.post("/jobs/{job_id}/recut", response_model=JobCreateResponse)
async def recut_job(job_id: str, payload: RecutRequest, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    job_repo = JobRepo(db)
    job = job_repo.get(job_id)
    if not job:
        raise NOT_FOUND
    job.status = JobStatus.QUEUED
    db.commit()
    enqueue_job(job.id)
    status_enum = job.status if isinstance(job.status, JobStatus) else JobStatus(job.status)
    return JobCreateResponse(
        job_id=job.id,
        status=status_enum,
        created_at=job.created_at,
        params=JobParams(
            max_clips=payload.max_clips or settings.llm_max_clips,
            min_clip_sec=payload.min_clip_sec or settings.min_clip_sec,
            max_clip_sec=payload.max_clip_sec or settings.max_clip_sec,
            target_aspect=settings.target_aspect,
            burn_subtitles=settings.burn_subtitles,
            language=settings.language,
            llm_style=payload.llm_style or "default",
        ),
    )


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str, db=Depends(get_db), api_key: str = Depends(require_api_key)) -> dict[str, str]:
    job_repo = JobRepo(db)
    job = job_repo.get(job_id)
    if not job:
        raise NOT_FOUND
    job_repo.delete(job)
    db.commit()
    return {"status": "deleted"}


__all__ = ["app"]
