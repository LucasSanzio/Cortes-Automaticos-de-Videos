"""Configuração do SQLAlchemy e sessão de banco."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..config import get_settings


Base = declarative_base()


def _db_path() -> str:
    settings = get_settings()
    db_file = Path(settings.data_dir) / "app.sqlite3"
    return f"sqlite:///{db_file}"


def get_engine():
    connect_args = {"check_same_thread": False}
    return create_engine(_db_path(), connect_args=connect_args, future=True)


engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Fornece um escopo transacional simples."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - re-lançamos para testes cobrirem
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Cria as tabelas, se necessário."""

    Base.metadata.create_all(bind=engine)


__all__ = ["Base", "SessionLocal", "session_scope", "init_db", "engine"]
