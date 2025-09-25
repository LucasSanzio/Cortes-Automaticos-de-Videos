"""Repositórios que encapsulam o acesso ao banco de dados."""
from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Clip, Job, JobStatus


class JobRepo:
    """Operações relacionadas a Jobs."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, job: Job) -> Job:
        self.session.add(job)
        self.session.flush()
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self.session.get(Job, job_id)

    def list_pending(self) -> Iterable[Job]:
        stmt = select(Job).where(Job.status != JobStatus.DONE)
        return self.session.execute(stmt).scalars().all()

    def delete(self, job: Job) -> None:
        self.session.delete(job)


class ClipRepo:
    """Operações relacionadas aos clipes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, clip: Clip) -> Clip:
        self.session.add(clip)
        self.session.flush()
        return clip

    def list_by_job(self, job_id: str) -> Iterable[Clip]:
        stmt = select(Clip).where(Clip.job_id == job_id)
        return self.session.execute(stmt).scalars().all()


__all__ = ["JobRepo", "ClipRepo"]
