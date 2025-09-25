import shutil

import pytest

from app.transcription.base import TranscriptSegment
from app.video.cutter import cut_clip


def test_cut_clip(tmp_path):
    source = tmp_path / 'source.mp4'
    if shutil.which('ffmpeg') is None:
        pytest.skip('ffmpeg não disponível')

    cmd = [
        'ffmpeg',
        '-y',
        '-f',
        'lavfi',
        '-i',
        'sine=frequency=800:duration=6',
        '-f',
        'lavfi',
        '-i',
        'color=c=green:s=640x360:d=6',
        '-shortest',
        str(source)
    ]
    import subprocess

    subprocess.run(cmd, check=True, capture_output=True)

    dest = tmp_path / 'out'
    segments = [TranscriptSegment(start=0.0, end=6.0, text='Teste')]
    result = cut_clip(source, dest, 1.0, 4.0, segments, '16:9', burn_subtitles=False)

    assert result.video_path.exists()
    assert result.srt_path.exists()
    assert result.vtt_path.exists()
    assert result.thumbnail_path.exists()
