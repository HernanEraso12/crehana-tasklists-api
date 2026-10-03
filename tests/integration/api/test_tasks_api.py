"""CRUD de tareas bajo /api/v1/lists/{list_id}/tasks (docs/04-api.md).
Mismo esquema que el ciclo de listas: TestClient sobre la app real y
SQLite en memoria, solo se sobrescribe get_db_session. El endpoint de
cambio de estado y el listado filtrado no son parte de este ciclo."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.api.dependencies import get_db_session
from app.infrastructure.persistence.database import Base
from app.main import app
from tests.integration.persistence.sqlite_support import create_in_memory_sqlite_engine

pytestmark = pytest.mark.integration


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


def _create_list(client: TestClient, name: str = "Sprint 12") -> dict:
    response = client.post("/api/v1/lists", json={"name": name})
    assert response.status_code == 201
    return response.json()


def _create_task(
    client: TestClient, list_id: str, title: str = "Escribir tests", **extra
) -> dict:
    payload = {"title": title, **extra}
    response = client.post(f"/api/v1/lists/{list_id}/tasks", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_returns_201_with_defaults_and_location_header(
    client: TestClient,
) -> None:
    task_list = _create_list(client)

    response = client.post(
        f"/api/v1/lists/{task_list['id']}/tasks",
        json={"title": "Escribir tests"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["priority"] == "MEDIUM"
    assert body["list_id"] == task_list["id"]
    assert (
        response.headers["location"]
        == f"/api/v1/lists/{task_list['id']}/tasks/{body['id']}"
    )


def test_create_with_high_priority_respects_it(client: TestClient) -> None:
    task_list = _create_list(client)

    response = client.post(
        f"/api/v1/lists/{task_list['id']}/tasks",
        json={"title": "Escribir tests", "priority": "HIGH"},
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "HIGH"


@pytest.mark.parametrize(
    "payload",
    [
        {"title": ""},
        {"title": "   "},
        {},
    ],
)
def test_create_rejects_invalid_title(client: TestClient, payload: dict) -> None:
    task_list = _create_list(client)

    response = client.post(f"/api/v1/lists/{task_list['id']}/tasks", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_rejects_invalid_priority(client: TestClient) -> None:
    task_list = _create_list(client)

    response = client.post(
        f"/api/v1/lists/{task_list['id']}/tasks",
        json={"title": "Escribir tests", "priority": "URGENTE"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_in_missing_list_returns_404_task_list_not_found(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/lists/00000000-0000-0000-0000-000000000000/tasks",
        json={"title": "Escribir tests"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_LIST_NOT_FOUND"


def test_get_returns_200(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    response = client.get(f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == task["id"]


def test_get_of_missing_task_returns_404_task_not_found(client: TestClient) -> None:
    task_list = _create_list(client)

    response = client.get(
        f"/api/v1/lists/{task_list['id']}/tasks/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_get_task_using_another_real_lists_id_returns_404(
    client: TestClient,
) -> None:
    task_list = _create_list(client, name="Lista A")
    other_list = _create_list(client, name="Lista B")
    task = _create_task(client, task_list["id"])

    response = client.get(f"/api/v1/lists/{other_list['id']}/tasks/{task['id']}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_patch_partial_keeps_unset_fields(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"], description="Original", priority="LOW")

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}",
        json={"title": "Escribir tests v2"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Escribir tests v2"
    assert body["description"] == "Original"
    assert body["priority"] == "LOW"


def test_patch_with_status_field_returns_422(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}",
        json={"status": "COMPLETED"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_patch_with_empty_body_returns_422(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    response = client.patch(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}", json={}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_delete_returns_204_and_subsequent_get_is_404(client: TestClient) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    delete_response = client.delete(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}"
    )
    get_response = client.get(f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
    assert get_response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_delete_of_task_from_another_list_returns_404_and_survives(
    client: TestClient,
) -> None:
    task_list = _create_list(client, name="Lista A")
    other_list = _create_list(client, name="Lista B")
    task = _create_task(client, task_list["id"])

    response = client.delete(f"/api/v1/lists/{other_list['id']}/tasks/{task['id']}")
    survivor = client.get(f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"
    assert survivor.status_code == 200


def test_deleting_the_list_cascades_to_its_task_end_to_end(
    client: TestClient,
) -> None:
    task_list = _create_list(client)
    task = _create_task(client, task_list["id"])

    delete_list_response = client.delete(f"/api/v1/lists/{task_list['id']}")
    get_task_response = client.get(
        f"/api/v1/lists/{task_list['id']}/tasks/{task['id']}"
    )

    assert delete_list_response.status_code == 204
    assert get_task_response.status_code == 404
