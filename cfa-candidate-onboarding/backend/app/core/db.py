"""Postgres engine/session management and audit-friendly helpers."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

_settings = get_settings()
engine = create_engine(_settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional scope; rolls back on error so partial audit rows are never committed."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Iterator[Session]:
    with session_scope() as session:
        yield session


def database_available() -> bool:
    try:
        with engine.connect():
            return True
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning("Postgres unavailable: %s", exc)
        return False
