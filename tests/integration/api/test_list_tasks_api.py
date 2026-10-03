"""GET /api/v1/lists/{list_id}/tasks: filtros (C4), paginación (C5) y
completion_percentage global (C7, C8). Todos los datos se crean por la
API (POST y PATCH .../status), nunca tocando la BD directamente."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def _create_list(client: TestClient, name: str = "Sprint 12") -> dict:
    response = client.post("/api/v1/lists", json={"name": name})
    assert response.status_code == 201
    return response.json()


def _create_task(client: TestClient, list_id: str, title: str, **extra) -> dict:
    payload = {"title": title, **extra}
    response = client.post(f"/api/v1/lists/{list_id}/tasks", json=payload)
    assert response.status_code == 201
    return response.json()


def _complete(client: TestClient, list_id: str, task_id: str) -> None:
    response = client.patch(
        f"/api/v1/lists/{list_id}/tasks/{task_id}/status",
        json={"status": "COMPLETED"},
    )
    assert response.status_code == 200


def test_list_without_tasks_returns_empty_page_and_zero_completion(
    client: TestClient,
) -> None:
    task_list = _create_list(client)

    response = client.get(f"/api/v1/lists/{task_list['id']}/tasks")

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["limit"] == 20
    assert body["offset"] == 0
    assert body["completion_percentage"] == 0.0


def test_without_filters_returns_all_tasks(client: TestClient) -> None:
    task_list = _create_list(client)
    _create_task(client, task_list["id"], "A")
    _create_task(client, task_list["id"], "B")

    response = client.get(f"/api/v1/lists/{task_list['id']}/tasks")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["title"] for item in body["items"]} == {"A", "B"}


def test_filters_by_status(client: TestClient) -> None:
    task_list = _create_list(client)
    pending = _create_task(client, task_list["id"], "Pending")
    completed = _create_task(client, task_list["id"], "Completed")
    _complete(client, task_list["id"], completed["id"])

    response = client.get(
        f"/api/v1/lists/{task_list['id']}/tasks", params={"status": "COMPLETED"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Completed"
    assert pending["title"] == "Pending"  # pista: no aparece en el filtrado


def test_filters_by_priority(client: TestClient) -> None:
    task_list = _create_list(client)
    _create_task(client, task_list["id"], "Low", priority="LOW")
    _create_task(client, task_list["id"], "High", priority="HIGH")

    response = client.get(
        f"/api/v1/lists/{task_list['id']}/tasks", params={"priority": "HIGH"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "High"


def test_combines_status_and_priority_filters_and_total_reflects_it(
    client: TestClient,
) -> None:
    task_list = _create_list(client)
    match = _create_task(client, task_list["id"], "Match", priority="HIGH")
    _complete(client, task_list["id"], match["id"])
    only_status = _create_task(client, task_list["id"], "OnlyStatus", priority="LOW")
    _complete(client, task_list["id"], only_status["id"])
    _create_task(client, task_list["id"], "OnlyPriority", priority="HIGH")

    response = client.get(
        f"/api/v1/lists/{task_list['id']}/tasks",
        params={"status": "COMPLETED", "priority": "HIGH"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Match"


def test_completion_percentage_is_global_and_ignores_filters(
    client: TestClient,
) -> None:
    task_list = _create_list(client)
    completed = _create_task(client, task_list["id"], "Completed", priority="HIGH")
    _complete(client, task_list["id"], completed["id"])
    _create_task(client, task_list["id"], "Pending1", priority="LOW")
    _create_task(client, task_list["id"], "Pending2", priority="LOW")

    unfiltered = client.get(f"/api/v1/lists/{task_list['id']}/tasks")
    filtered = client.get(
        f"/api/v1/lists/{task_list['id']}/tasks", params={"priority": "LOW"}
    )

    assert unfiltered.json()["completion_percentage"] == 33.33
    # El filtro por priority=LOW deja 2 de 3 tareas (total cambia),
    # pero la completitud sigue siendo la de toda la lista.
    assert filtered.json()["total"] == 2
    assert filtered.json()["completion_percentage"] == 33.33


def test_paginates_with_limit_and_offset(client: TestClient) -> None:
    task_list = _create_list(client)
    _create_task(client, task_list["id"], "A")
    _create_task(client, task_list["id"], "B")
    _create_task(client, task_list["id"], "C")

    first_page = client.get(
        f"/api/v1/lists/{task_list['id']}/tasks", params={"limit": 2, "offset": 0}
    )
    second_page = client.get(
        f"/api/v1/lists/{task_list['id']}/tasks", params={"limit": 2, "offset": 2}
    )

    assert first_page.json()["total"] == 3
    assert len(first_page.json()["items"]) == 2
    assert len(second_page.json()["items"]) == 1


def test_does_not_include_tasks_from_another_real_list(client: TestClient) -> None:
    task_list = _create_list(client, name="Lista A")
    other_list = _create_list(client, name="Lista B")
    _create_task(client, task_list["id"], "Mine")
    _create_task(client, other_list["id"], "Other")

    response = client.get(f"/api/v1/lists/{task_list['id']}/tasks")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Mine"


@pytest.mark.parametrize(
    "query",
    [
        {"status": "URGENTE"},
        {"priority": "URGENTE"},
    ],
)
def test_rejects_invalid_filter_values(client: TestClient, query: dict) -> None:
    task_list = _create_list(client)

    response = client.get(f"/api/v1/lists/{task_list['id']}/tasks", params=query)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    "query",
    [
        {"limit": 101},
        {"offset": -1},
    ],
)
def test_rejects_out_of_range_pagination(client: TestClient, query: dict) -> None:
    task_list = _create_list(client)

    response = client.get(f"/api/v1/lists/{task_list['id']}/tasks", params=query)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_missing_list_returns_404_task_list_not_found(client: TestClient) -> None:
    missing_list_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(f"/api/v1/lists/{missing_list_id}/tasks")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_LIST_NOT_FOUND"
