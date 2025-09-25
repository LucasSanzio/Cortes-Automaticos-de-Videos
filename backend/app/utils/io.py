"""Funções utilitárias para arquivos."""
from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Iterable


def allowed_extension(filename: str, allowed: Iterable[str]) -> bool:
    suffix = Path(filename).suffix.lower().lstrip(".")
    return suffix in {ext.lower() for ext in allowed}


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    return mime or "application/octet-stream"


__all__ = ["allowed_extension", "guess_mime"]
