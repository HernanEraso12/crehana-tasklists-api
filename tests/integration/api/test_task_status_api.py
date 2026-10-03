"""PATCH /api/v1/lists/{list_id}/tasks/{task_id}/status (B2, C3,
docs/04-api.md). Mismo esquema que los demás ciclos de API: fixture
`client` compartido en conftest.py."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def _create_list(client: TestClient, name: str = "Sprint 12") -> dict:
    response = client.post("/api/v1/lists", json={"name": name})
    assert response.status_code == 201
    return response.json()


def _create_task(client: TestClient, list_id: str, **extra) -> dict:
    payload = {"title": "Escribir tests", **extra}
    response = client.post(f"/api/v1/lists/{list_id}/tasks", json=payload)
    assert response.status_code == 201
    return response.json()


def test_changes_status_and_returns_200(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}/status",
        json={"status": "COMPLETED"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_allows_completed_to_pending(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])
    client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}/status",
        json={"status": "COMPLETED"},
    )

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}/status",
        json={"status": "PENDING"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"


def test_same_status_is_idempotent_and_returns_200(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}/status",
        json={"status": "PENDING"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"


def test_rejects_invalid_status_value(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}/status",
        json={"status": "URGENTE"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_missing_status_field_returns_422(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}/status", json={}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_missing_task_returns_404_task_not_found(client: TestClient) -> None:
    task_list = _create_list(client)

    missing_task_id = "00000000-0000-0000-0000-000000000000"
    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{missing_task_id}/status",
        json={"status": "COMPLETED"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_task_from_another_real_list_returns_404(client: TestClient) -> None:
    task_list = _create_list(client, name="Lista A")
    other_list = _create_list(client, name="Lista B")
    task = _create_task(client, task_list["id"])

    response = client.patch(
        f"/api/v1/lists/{other_list['id']}/tasks/{task['id']}/status",
        json={"status": "COMPLETED"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_missing_list_returns_404_task_list_not_found(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/lists/00000000-0000-0000-0000-000000000000"
        "/tasks/00000000-0000-0000-0000-000000000000/status",
        json={"status": "COMPLETED"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_LIST_NOT_FOUND"


def test_extra_field_in_body_returns_422(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}/status",
        json={"status": "COMPLETED", "title": "No debería aceptarse"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
