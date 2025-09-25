"""Definição de erros estruturados da API."""
from __future__ import annotations

from fastapi import HTTPException, status


class APIError(HTTPException):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


INVALID_FILE = APIError("INVALID_FILE", "Arquivo inválido", status.HTTP_400_BAD_REQUEST)
UNSUPPORTED_MEDIA = APIError("UNSUPPORTED_MEDIA", "Mídia não suportada", status.HTTP_400_BAD_REQUEST)
NOT_FOUND = APIError("NOT_FOUND", "Registro não encontrado", status.HTTP_404_NOT_FOUND)
RATE_LIMITED = APIError("RATE_LIMITED", "Limite de requisições atingido", status.HTTP_429_TOO_MANY_REQUESTS)


__all__ = ["APIError", "INVALID_FILE", "UNSUPPORTED_MEDIA", "NOT_FOUND", "RATE_LIMITED"]
