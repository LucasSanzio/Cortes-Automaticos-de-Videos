"""Implementação simples de transcrição local.

Sempre que a biblioteca `whisper` estiver disponível o áudio será processado
utilizando o modelo solicitado. Caso contrário retornamos uma transcrição
simplificada baseada na duração do vídeo. Essa abordagem permite que o sistema
funcione em ambientes sem GPU durante testes automatizados.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from .base import TranscriptResult, TranscriptSegment, TranscriptionProvider


def _probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


class LocalWhisperProvider(TranscriptionProvider):
    """Transcreve mídia usando openai-whisper quando disponível."""

    def __init__(self, model: str = "small") -> None:
        self.model = model

    def transcribe(self, media_path: Path, language: str) -> TranscriptResult:
        try:
            import whisper  # type: ignore

            model = whisper.load_model(self.model)
            transcription = model.transcribe(str(media_path), language=language)
            segments: List[TranscriptSegment] = []
            for segment in transcription.get("segments", []):
                segments.append(
                    TranscriptSegment(
                        start=float(segment.get("start", 0.0)),
                        end=float(segment.get("end", 0.0)),
                        text=str(segment.get("text", "")).strip(),
                    )
                )
            duration = float(transcription.get("duration") or _probe_duration(media_path))
            return TranscriptResult(duration=duration, segments=segments)
        except ModuleNotFoundError:
            # Fallback extremamente simples baseado apenas na duração
            duration = _probe_duration(media_path)
            text = "Transcrição automática indisponível no ambiente de teste."
            segments = [TranscriptSegment(start=0.0, end=duration, text=text)]
            return TranscriptResult(duration=duration, segments=segments)


__all__ = ["LocalWhisperProvider"]
