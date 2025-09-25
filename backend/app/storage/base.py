"""Definições de interface de storage."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class StoredFile:
    path: str
    public_url: str | None


class StorageProvider(Protocol):
    def save(self, source: Path, dest: str) -> StoredFile:
        ...

    def delete(self, path: str) -> None:
        ...


