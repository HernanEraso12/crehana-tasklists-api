"""API de invitaciones a una lista (E3, docs/04-api.md). Dispara el
Notifier ficticio (E2) vía `LoggingNotifier`; no hay estado que leer
después, así que se prueba el código de respuesta y el cuerpo."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def _create_list(client: TestClient, name: str = "Sprint 12") -> dict:
    response = client.post("/api/v1/lists", json={"name": name})
    assert response.status_code == 201
    return response.json()


def test_invite_to_existing_list_returns_202(client: TestClient) -> None:
    created = _create_list(client)

    response = client.post(
        f"/api/v1/lists/{created['id']}/invitations",
        json={"email": "colega@example.com"},
    )

    assert response.status_code == 202
    assert response.json() == {
        "list_id": created["id"],
        "email": "colega@example.com",
    }


def test_invite_to_missing_list_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/lists/00000000-0000-0000-0000-000000000000/invitations",
        json={"email": "colega@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_LIST_NOT_FOUND"


def test_invite_with_invalid_email_returns_422(client: TestClient) -> None:
    created = _create_list(client)

    response = client.post(
        f"/api/v1/lists/{created['id']}/invitations",
        json={"email": "not-an-email"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
