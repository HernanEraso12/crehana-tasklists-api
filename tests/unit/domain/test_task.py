"""Crear Task con estado inicial PENDING, prioridad por defecto MEDIUM (B1, B3)
y validación del título según B6: obligatorio, 1-200 caracteres tras recortar.
También: change_status permite cualquier transición, es idempotente con el
mismo estado y actualiza updated_at (B2). Y: update(...) actualiza
parcialmente título/descripción/prioridad (C2, C3: no acepta status),
valida el título igual que al crear y solo toca updated_at si algo
cambió."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domain import clock
from app.domain.enums import Priority, TaskStatus
from app.domain.exceptions import InvalidTaskError
from app.domain.task import Task

pytestmark = pytest.mark.unit


def test_creates_task_with_default_status_and_priority() -> None:
    task = Task(title="Escribir tests", list_id=uuid4())

    assert task.status == TaskStatus.PENDING
    assert task.priority == Priority.MEDIUM


def test_creates_task_with_explicit_priority() -> None:
    task = Task(title="Escribir tests", list_id=uuid4(), priority=Priority.HIGH)

    assert task.priority == Priority.HIGH


def test_strips_leading_and_trailing_spaces_in_title() -> None:
    task = Task(title=" Escribir tests ", list_id=uuid4())

    assert task.title == "Escribir tests"


def test_rejects_empty_title() -> None:
    with pytest.raises(InvalidTaskError):
        Task(title="", list_id=uuid4())


def test_rejects_whitespace_only_title() -> None:
    with pytest.raises(InvalidTaskError):
        Task(title="   ", list_id=uuid4())


def test_rejects_title_longer_than_200_characters() -> None:
    with pytest.raises(InvalidTaskError):
        Task(title="a" * 201, list_id=uuid4())


def test_accepts_title_of_exactly_200_characters() -> None:
    task = Task(title="a" * 200, list_id=uuid4())

    assert len(task.title) == 200


def test_change_status_updates_the_status() -> None:
    task = Task(title="Escribir tests", list_id=uuid4())

    task.change_status(TaskStatus.IN_PROGRESS)

    assert task.status == TaskStatus.IN_PROGRESS


def test_change_status_allows_completed_to_pending() -> None:
    task = Task(title="Escribir tests", list_id=uuid4(), status=TaskStatus.COMPLETED)

    task.change_status(TaskStatus.PENDING)

    assert task.status == TaskStatus.PENDING


def test_change_status_is_idempotent_with_the_same_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    creation_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "utcnow", lambda: creation_time)
    task = Task(title="Escribir tests", list_id=uuid4(), status=TaskStatus.PENDING)

    monkeypatch.setattr(
        clock, "utcnow", lambda: datetime(2026, 1, 2, tzinfo=timezone.utc)
    )
    task.change_status(TaskStatus.PENDING)

    assert task.status == TaskStatus.PENDING
    assert task.updated_at == creation_time


def test_change_status_updates_updated_at(monkeypatch: pytest.MonkeyPatch) -> None:
    creation_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "utcnow", lambda: creation_time)
    task = Task(title="Escribir tests", list_id=uuid4())
    assert task.updated_at == creation_time

    later_time = datetime(2026, 1, 2, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "utcnow", lambda: later_time)
    task.change_status(TaskStatus.IN_PROGRESS)

    assert task.updated_at == later_time


def test_update_changes_title_and_keeps_description_priority_and_status() -> None:
    task = Task(
        title="Escribir tests",
        list_id=uuid4(),
        description="Original",
        priority=Priority.LOW,
        status=TaskStatus.IN_PROGRESS,
    )

    task.update(title="Escribir tests v2")

    assert task.title == "Escribir tests v2"
    assert task.description == "Original"
    assert task.priority == Priority.LOW
    assert task.status == TaskStatus.IN_PROGRESS


def test_update_changes_priority() -> None:
    task = Task(title="Escribir tests", list_id=uuid4(), priority=Priority.LOW)

    task.update(priority=Priority.HIGH)

    assert task.priority == Priority.HIGH


def test_update_clears_description_with_none() -> None:
    task = Task(title="Escribir tests", list_id=uuid4(), description="Original")

    task.update(description=None)

    assert task.description is None


def test_update_rejects_invalid_title_without_changing_anything() -> None:
    task = Task(title="Escribir tests", list_id=uuid4(), description="Original")

    with pytest.raises(InvalidTaskError):
        task.update(title="   ")

    assert task.title == "Escribir tests"
    assert task.description == "Original"


def test_update_only_touches_updated_at_when_something_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    creation_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "utcnow", lambda: creation_time)
    task = Task(title="Escribir tests", list_id=uuid4())

    later_time = datetime(2026, 1, 2, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "utcnow", lambda: later_time)
    task.update()  # sin argumentos: nada cambia

    assert task.updated_at == creation_time

    task.update(title="Escribir tests v2")

    assert task.updated_at == later_time
