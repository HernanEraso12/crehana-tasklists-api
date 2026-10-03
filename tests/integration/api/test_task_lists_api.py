"""API de listas bajo /api/v1 (docs/04-api.md). TestClient sobre la
app real y SQLite en memoria: se sobrescribe la dependencia de sesión
(`get_db_session`), nunca los casos de uso ni los repositorios. La
sesión es una por request: commit si todo sale bien, rollback si hay
error (se prueba que lo creado en un request se lee en el siguiente)."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def _create_list(client: TestClient, name: str = "Sprint 12", **extra) -> dict:
    payload = {"name": name, **extra}
    response = client.post("/api/v1/lists", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_returns_201_with_body_and_location_header(client: TestClient) -> None:
    response = client.post(
        "/api/v1/lists", json={"name": "Sprint 12", "description": "Opcional"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Sprint 12"
    assert body["description"] == "Opcional"
    assert "id" in body
    assert response.headers["location"] == f"/api/v1/lists/{body['id']}"


@pytest.mark.parametrize(
    "payload",
    [
        {"name": ""},
        {"name": "   "},
        {},
    ],
)
def test_create_rejects_invalid_name(client: TestClient, payload: dict) -> None:
    response = client.post("/api/v1/lists", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_returns_200(client: TestClient) -> None:
    created = _create_list(client)

    response = client.get(f"/api/v1/lists/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_of_missing_id_returns_404_task_list_not_found(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/lists/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_LIST_NOT_FOUND"


def test_get_with_malformed_uuid_returns_422(client: TestClient) -> None:
    response = client.get("/api/v1/lists/not-a-uuid")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_list_returns_200_with_pagination_envelope(client: TestClient) -> None:
    _create_list(client, name="A")
    _create_list(client, name="B")

    response = client.get("/api/v1/lists")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["limit"] == 20
    assert body["offset"] == 0
    assert len(body["items"]) == 2


@pytest.mark.parametrize(
    "query",
    [
        {"limit": 101},
        {"offset": -1},
    ],
)
def test_list_rejects_out_of_range_pagination(client: TestClient, query: dict) -> None:
    response = client.get("/api/v1/lists", params=query)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_patch_partial_keeps_unset_fields(client: TestClient) -> None:
    created = _create_list(client, name="Sprint 12", description="Original")

    response = client.patch(
        f"/api/v1/lists/{created['id']}", json={"name": "Sprint 13"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Sprint 13"
    assert body["description"] == "Original"


def test_patch_with_description_null_clears_it(client: TestClient) -> None:
    created = _create_list(client, name="Sprint 12", description="Original")

    response = client.patch(
        f"/api/v1/lists/{created['id']}", json={"description": None}
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_patch_with_empty_body_returns_422(client: TestClient) -> None:
    created = _create_list(client)

    response = client.patch(f"/api/v1/lists/{created['id']}", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_patch_of_missing_id_returns_404(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/lists/00000000-0000-0000-0000-000000000000",
        json={"name": "Sprint 13"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_LIST_NOT_FOUND"


def test_delete_returns_204_and_subsequent_get_is_404(client: TestClient) -> None:
    created = _create_list(client)

    delete_response = client.delete(f"/api/v1/lists/{created['id']}")
    get_response = client.get(f"/api/v1/lists/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
    assert get_response.json()["error"]["code"] == "TASK_LIST_NOT_FOUND"


def test_delete_of_missing_id_returns_404(client: TestClient) -> None:
    response = client.delete("/api/v1/lists/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_LIST_NOT_FOUND"


def test_what_is_created_in_one_request_is_readable_in_the_next(
    client: TestClient,
) -> None:
    """Prueba el commit por request: cada llamada a client.* es un
    request HTTP independiente, con su propia sesión."""
    created = _create_list(client, name="Sprint 12")

    response = client.get(f"/api/v1/lists/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Sprint 12"
