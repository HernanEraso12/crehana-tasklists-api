"""Fixture compartido por las suites de integración de la API:
TestClient sobre la app real y SQLite en memoria, sobrescribiendo solo
la dependencia de sesión (`get_db_session`) — nunca los casos de uso
ni los repositorios. La sesión es una por request: commit si todo sale
bien, rollback si hay error."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.api.dependencies import get_db_session
from app.infrastructure.persistence.database import Base
from app.main import app
from tests.integration.persistence.sqlite_support import create_in_memory_sqlite_engine


@pytest.fixture
def client() -> TestClient:
    engine = create_in_memory_sqlite_engine()
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
