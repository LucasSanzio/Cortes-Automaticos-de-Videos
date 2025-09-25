"""Configuração da fila RQ."""
from __future__ import annotations

from rq import Queue
from rq.job import Job
from rq.worker import SimpleWorker

from ..config import get_settings
from . import tasks


settings = get_settings()
queue = Queue(name=settings.queue_name, connection=tasks.get_redis())


def enqueue_job(job_id: str) -> Job:
    return queue.enqueue(tasks.process_job, job_id, job_timeout=60 * 60 * 6)


def run_worker() -> None:
    worker = SimpleWorker([queue], connection=tasks.get_redis())
    worker.work(with_scheduler=True)


if __name__ == "__main__":  # pragma: no cover - ponto de entrada do worker
    run_worker()


__all__ = ["enqueue_job", "run_worker", "queue"]
