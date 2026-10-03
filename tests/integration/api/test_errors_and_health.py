"""Huecos del formato de error único (C9) y /health (C12). Reutiliza
el fixture `client` de conftest.py, salvo donde se necesita un
TestClient propio (raise_server_exceptions=False) para ver la
respuesta real de un error no controlado en vez de que se relance en
el proceso de test."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.infrastructure.api.dependencies import get_db_session, get_task_list_repository
from app.main import app

pytestmark = pytest.mark.integration


def test_unhandled_exception_returns_500_without_leaking_internals(
    client: TestClient,
) -> None:
    secret_message = "boom: conexión interna a xyz-internal-service falló"

    def _broken_repository():
        raise RuntimeError(secret_message)

    app.dependency_overrides[get_task_list_repository] = _broken_repository
    try:
        broken_client = TestClient(app, raise_server_exceptions=False)
        response = broken_client.get("/api/v1/lists")
    finally:
        del app.dependency_overrides[get_task_list_repository]

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert secret_message not in response.text
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text


def test_validation_error_details_include_the_failing_field(
    client: TestClient,
) -> None:
    response = client.post("/api/v1/lists", json={})

    assert response.status_code == 422
    details = response.json()["error"]["details"]
    assert isinstance(details, list)
    assert any("name" in error["loc"] for error in details)


def test_domain_not_found_error_has_null_details(client: TestClient) -> None:
    response = client.get("/api/v1/lists/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["error"]["details"] is None


def test_health_returns_200_when_database_is_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_503_when_database_fails(client: TestClient) -> None:
    def _broken_db_session():
        raise OperationalError("SELECT 1", {}, Exception("DB down"))

    app.dependency_overrides[get_db_session] = _broken_db_session
    try:
        response = client.get("/health")
    finally:
        del app.dependency_overrides[get_db_session]

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SERVICE_UNAVAILABLE"
