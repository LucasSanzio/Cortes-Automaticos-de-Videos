import shutil

import pytest

from app.transcription.whisper_local import LocalWhisperProvider


def test_local_transcription_fallback(tmp_path):
    media = tmp_path / 'test.mp4'
    if shutil.which('ffmpeg') is None:
        pytest.skip('ffmpeg não disponível')

    cmd = [
        'ffmpeg',
        '-y',
        '-f',
        'lavfi',
        '-i',
        'sine=frequency=500:duration=2',
        '-f',
        'lavfi',
        '-i',
        'color=c=red:s=320x240:d=2',
        '-shortest',
        str(media)
    ]
    import subprocess

    subprocess.run(cmd, check=True, capture_output=True)
    provider = LocalWhisperProvider('tiny')
    result = provider.transcribe(media, language='pt')
    assert result.duration > 0
    assert result.segments
