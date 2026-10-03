"""Composition root de la API: cablea repositorios y casos de uso con
`Depends`. Es el único lugar de `infrastructure` que conoce tanto
`infrastructure/persistence` como `application`.

La sesión es una por request: `commit` si todo sale bien, `rollback`
si hay una excepción, siempre se cierra (A5, D4)."""

from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.infrastructure.config import Settings
from app.infrastructure.persistence.database import (
    create_session_factory,
    create_sqlalchemy_engine,
)

_settings = Settings()
_engine = create_sqlalchemy_engine(_settings.database_url)
_session_factory = create_session_factory(_engine)


def get_db_session() -> Iterator[Session]:
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
