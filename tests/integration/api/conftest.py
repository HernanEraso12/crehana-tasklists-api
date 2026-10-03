"""Fixture compartido por las suites de integración de la API:
TestClient sobre la app real, sobrescribiendo solo la dependencia de
sesión (`get_db_session`) — nunca los casos de uso ni los
repositorios. La sesión es una por request: commit si todo sale bien,
rollback si hay error.

BD: SQLite en memoria por defecto, o PostgreSQL real si
`TEST_DATABASE_URL` está definida (CI, job `tests-postgres`, A7)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.api.dependencies import get_db_session
from app.infrastructure.persistence.database import Base
from app.main import app
from tests.integration.persistence.sqlite_support import create_test_engine


@pytest.fixture
def client() -> TestClient:
    engine = create_test_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def _override_get_db_session():
        session = Session(engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = _override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    # Cada request ya cierra su sesión (get_db_session), pero el motor
    # en sí (con su pool de conexiones) solo se libera aquí. Contra
    # Postgres real esto evita acumular conexiones entre tests.
    engine.dispose()
