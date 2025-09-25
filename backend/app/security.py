"""Módulo responsável por autenticação baseada em API Key."""
from __future__ import annotations

from fastapi import Header, HTTPException, status

from .config import get_settings


API_KEY_HEADER = "X-API-Key"


def require_api_key(x_api_key: str = Header(..., alias=API_KEY_HEADER)) -> str:
    """Valida o header de API Key."""

    settings = get_settings()
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "API_KEY_NOT_CONFIGURED", "message": "API Key não definida"},
        )

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_API_KEY", "message": "Chave inválida"},
        )
    return x_api_key


def optional_api_key(x_api_key: str | None = Header(None, alias=API_KEY_HEADER)) -> str | None:
    """Retorna a chave quando presente sem forçar autenticação.

    Utilizado em rotas públicas, como métricas, nas quais é interessante registrar
    a chave do chamador quando fornecida.
    """

    return x_api_key


__all__ = ["API_KEY_HEADER", "require_api_key", "optional_api_key"]
