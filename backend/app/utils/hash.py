"""Geração de hash para arquivos."""
from __future__ import annotations

import hashlib
from pathlib import Path


def file_checksum(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


__all__ = ["file_checksum"]
