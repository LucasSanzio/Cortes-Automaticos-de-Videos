"""Storage local em disco."""
from __future__ import annotations

import shutil
from pathlib import Path

from ..config import get_settings
from .base import StoredFile, StorageProvider


class LocalStorage(StorageProvider):
    """Implementação simples usando o sistema de arquivos."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_path = Path(self.settings.data_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, source: Path, dest: str) -> StoredFile:
        dest_path = self.base_path / dest
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest_path)
        public_url = None
        if self.settings.public_base_url:
            base = str(self.settings.public_base_url).rstrip('/')
            public_url = f"{base}/{dest}".replace("//", "/")
            if public_url.startswith("http:/") and not public_url.startswith("http://"):
                public_url = public_url.replace("http:/", "http://")
            if public_url.startswith("https:/") and not public_url.startswith("https://"):
                public_url = public_url.replace("https:/", "https://")
        return StoredFile(path=str(dest), public_url=public_url)

    def delete(self, path: str) -> None:
        try:
            (self.base_path / path).unlink(missing_ok=True)
        except AttributeError:  # pragma: no cover - Python < 3.8
            file_path = self.base_path / path
            if file_path.exists():
                file_path.unlink()


__all__ = ["LocalStorage"]
