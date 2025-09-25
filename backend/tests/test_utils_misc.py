import os
from pathlib import Path

from app.storage.local import LocalStorage
from app.utils.hash import file_checksum
from app.utils.io import allowed_extension, guess_mime
from app.video.layout import build_scale_filter
from app.video.subtitles import write_srt, write_vtt


def test_allowed_extension_and_mime(tmp_path):
    assert allowed_extension('video.mp4', ['mp4'])
    assert not allowed_extension('video.mkv', ['mp4'])

    sample = tmp_path / 'sample.txt'
    sample.write_text('demo')
    assert guess_mime(sample) == 'text/plain'


def test_file_checksum(tmp_path):
    sample = tmp_path / 'file.bin'
    sample.write_bytes(b'abc123')
    checksum = file_checksum(sample)
    assert len(checksum) == 64


def test_local_storage_save_delete(tmp_path, monkeypatch):
    os.environ['DATA_DIR'] = str(tmp_path / 'data')
    from app.config import get_settings

    get_settings.cache_clear()
    storage = LocalStorage()
    src = tmp_path / 'input.bin'
    src.write_bytes(b'data')
    stored = storage.save(src, 'jobs/test/input.bin')
    assert Path(storage.base_path, stored.path).exists()
    storage.delete(stored.path)
    assert not Path(storage.base_path, stored.path).exists()


def test_build_scale_filter():
    layout = build_scale_filter(1280, 720, '9:16')
    assert 'crop' in layout.filters


def test_write_subtitles(tmp_path):
    from app.transcription.base import TranscriptSegment

    segments = [TranscriptSegment(start=0, end=2, text='Olá mundo')]
    srt = tmp_path / 'test.srt'
    vtt = tmp_path / 'test.vtt'
    write_srt(srt, segments)
    write_vtt(vtt, segments)
    assert 'Olá mundo' in srt.read_text(encoding='utf-8')
    assert 'Olá mundo' in vtt.read_text(encoding='utf-8')
