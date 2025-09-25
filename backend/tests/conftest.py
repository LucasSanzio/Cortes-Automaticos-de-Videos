import os
import shutil
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault('DATA_DIR', '/tmp/test-data')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
os.environ.setdefault('API_KEY', 'testkey')
os.environ.setdefault('PROMETHEUS_ENABLED', 'false')
os.environ.setdefault('LLM_MAX_CLIPS', '2')
os.environ.setdefault('RATE_LIMIT', '60/minute')

root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))
(root_dir / '.env').write_text('')

from app.main import app  # noqa: E402
from app.db.base import init_db  # noqa: E402
from app.config import get_settings  # noqa: E402

get_settings.cache_clear()
init_db()


@pytest.fixture()
def client(tmp_path, monkeypatch):
    data_dir = tmp_path / 'data'
    os.environ['DATA_DIR'] = str(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    get_settings.cache_clear()
    get_settings()

    monkeypatch.setattr('app.workers.queue.enqueue_job', lambda job_id: None)
    monkeypatch.setattr('app.workers.tasks.get_redis', lambda: None)
    monkeypatch.setattr('app.workers.progress.get_progress', lambda *args, **kwargs: None)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def sample_video(tmp_path):
    video = tmp_path / 'sample.mp4'
    cmd = [
        'ffmpeg',
        '-y',
        '-f',
        'lavfi',
        '-i',
        'sine=frequency=1000:duration=5',
        '-f',
        'lavfi',
        '-i',
        'color=c=blue:s=640x360:d=5',
        '-shortest',
        str(video)
    ]
    import subprocess

    if shutil.which('ffmpeg') is None:
        pytest.skip('ffmpeg não disponível no ambiente de testes')
    subprocess.run(cmd, check=True, capture_output=True)
    return video
