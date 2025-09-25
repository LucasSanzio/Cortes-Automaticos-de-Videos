"""Configurações da aplicação.

Todas as variáveis são carregadas de variáveis de ambiente para facilitar o uso
em produção. Os valores padrão são adequados para desenvolvimento local.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Representa as configurações globais da aplicação."""

    app_env: str = Field("dev", alias="APP_ENV")
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")
    api_key: str = Field("changeme", alias="API_KEY")
    rate_limit: str = Field("60/minute", alias="RATE_LIMIT")
    cors_origins: str = Field("http://localhost:3000", alias="CORS_ORIGINS")

    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    queue_name: str = Field("jobs", alias="QUEUE_NAME")
    max_workers: int = Field(1, alias="MAX_WORKERS")

    transcribe_provider: str = Field("local", alias="TRANSCRIBE_PROVIDER")
    whisper_model: str = Field("small", alias="WHISPER_MODEL")
    language: str = Field("pt", alias="LANGUAGE")

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    llm_model: str = Field("gpt-4o-mini", alias="LLM_MODEL")
    llm_temperature: float = Field(0.5, alias="LLM_TEMPERATURE")
    llm_max_clips: int = Field(5, alias="LLM_MAX_CLIPS")
    min_clip_sec: int = Field(20, alias="MIN_CLIP_SEC")
    max_clip_sec: int = Field(90, alias="MAX_CLIP_SEC")
    target_aspect: str = Field("16:9", alias="TARGET_ASPECT")
    burn_subtitles: bool = Field(True, alias="BURN_SUBTITLES")

    storage_provider: str = Field("local", alias="STORAGE_PROVIDER")
    data_dir: Path = Field(Path("/data"), alias="DATA_DIR")
    public_base_url: Optional[AnyHttpUrl] = Field(
        default="http://localhost:8000", alias="PUBLIC_BASE_URL"
    )

    s3_bucket: Optional[str] = Field(default=None, alias="S3_BUCKET")
    s3_region: Optional[str] = Field(default=None, alias="S3_REGION")
    s3_prefix: str = Field("jobs/", alias="S3_PREFIX")
    s3_presign_ttl_seconds: int = Field(86_400, alias="S3_PRESIGN_TTL_SECONDS")

    max_upload_mb: int = Field(2048, alias="MAX_UPLOAD_MB")
    allowed_ext: str = Field("mp4,mov,mkv", alias="ALLOWED_EXT")
    url_fetch_enabled: bool = Field(False, alias="URL_FETCH_ENABLED")
    webhook_enabled: bool = Field(False, alias="WEBHOOK_ENABLED")
    jwt_enabled: bool = Field(False, alias="JWT_ENABLED")
    retention_days: int = Field(7, alias="RETENTION_DAYS")

    prometheus_enabled: bool = Field(True, alias="PROMETHEUS_ENABLED")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    fast_cut: bool = Field(False, alias="FAST_CUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin]

    @validator("target_aspect")
    def validate_aspect(cls, value: str) -> str:  # noqa: D401
        """Garante que a razão esteja no formato suportado."""

        if value not in {"16:9", "9:16", "1:1"}:
            raise ValueError("TARGET_ASPECT deve ser 16:9, 9:16 ou 1:1")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna as configurações compartilhadas em cache."""

    settings = Settings()  # type: ignore[call-arg]
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings


__all__ = ["Settings", "get_settings"]
