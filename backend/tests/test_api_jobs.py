from fastapi.testclient import TestClient

from app.db.base import SessionLocal
from app.db.models import Job, JobStatus


def _auth_headers():
    return {'X-API-Key': 'testkey'}


def test_create_job_upload(client: TestClient, sample_video):
    with sample_video.open('rb') as f:
        response = client.post('/jobs', headers=_auth_headers(), files={'file': ('sample.mp4', f, 'video/mp4')})
    assert response.status_code == 200
    data = response.json()
    assert 'job_id' in data


def test_get_job_not_found(client: TestClient):
    response = client.get('/jobs/unknown', headers=_auth_headers())
    assert response.status_code == 404


def test_job_detail_after_processing(client: TestClient, sample_video):
    with sample_video.open('rb') as f:
        response = client.post('/jobs', headers=_auth_headers(), files={'file': ('sample.mp4', f, 'video/mp4')})
    job_id = response.json()['job_id']

    with SessionLocal() as session:
        job = session.get(Job, job_id)
        job.status = JobStatus.DONE
        session.commit()

    response = client.get(f'/jobs/{job_id}', headers=_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data['status'] in ['QUEUED', 'DONE']
