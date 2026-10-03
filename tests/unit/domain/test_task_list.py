"""Validación del nombre de TaskList (B5): obligatorio, 1-100 caracteres,
se recorta espacios al inicio o al final, no vacío tras recortar.
También: TaskList.update(...) actualiza parcialmente (C2), valida igual
que al crear y solo toca updated_at si algo cambió."""

from datetime import datetime, timezone

import pytest

from app.domain import clock
from app.domain.exceptions import InvalidTaskListError
from app.domain.task_list import TaskList

pytestmark = pytest.mark.unit


def test_creates_task_list_with_valid_name() -> None:
    task_list = TaskList(name="Sprint 12")

    assert task_list.name == "Sprint 12"


def test_rejects_empty_name() -> None:
    with pytest.raises(InvalidTaskListError):
        TaskList(name="")


def test_rejects_whitespace_only_name() -> None:
    with pytest.raises(InvalidTaskListError):
        TaskList(name="   ")


def test_strips_leading_and_trailing_spaces() -> None:
    task_list = TaskList(name=" Sprint ")

    assert task_list.name == "Sprint"


def test_rejects_name_longer_than_100_characters() -> None:
    with pytest.raises(InvalidTaskListError):
        TaskList(name="a" * 101)


def test_accepts_name_of_exactly_100_characters() -> None:
    task_list = TaskList(name="a" * 100)

    assert len(task_list.name) == 100


def test_update_changes_name_and_keeps_description() -> None:
    task_list = TaskList(name="Sprint 12", description="Original")

    task_list.update(name="Sprint 13")

    assert task_list.name == "Sprint 13"
    assert task_list.description == "Original"


def test_update_clears_description_with_none() -> None:
    task_list = TaskList(name="Sprint 12", description="Original")

    task_list.update(description=None)

    assert task_list.name == "Sprint 12"
    assert task_list.description is None


def test_update_without_arguments_keeps_everything_unchanged() -> None:
    task_list = TaskList(name="Sprint 12", description="Original")

    task_list.update()

    assert task_list.name == "Sprint 12"
    assert task_list.description == "Original"


def test_update_rejects_invalid_name_without_changing_anything() -> None:
    task_list = TaskList(name="Sprint 12", description="Original")

    with pytest.raises(InvalidTaskListError):
        task_list.update(name="   ")

    assert task_list.name == "Sprint 12"
    assert task_list.description == "Original"


def test_created_at_and_updated_at_are_identical_on_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Dos valores distintos en llamadas sucesivas: si el reloj se
    # llamara dos veces (una por campo), created_at y updated_at
    # tomarían el primer y el segundo valor respectivamente, y no
    # coincidirían. Solo pasan si se llama una sola vez.
    timestamps = iter(
        [
            datetime(2026, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 0, 0, 0, 500, tzinfo=timezone.utc),
        ]
    )
    monkeypatch.setattr(clock, "utcnow", lambda: next(timestamps))

    task_list = TaskList(name="Sprint 12")

    assert task_list.created_at == task_list.updated_at


def test_update_only_touches_updated_at_when_something_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    creation_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "utcnow", lambda: creation_time)
    task_list = TaskList(name="Sprint 12")

    later_time = datetime(2026, 1, 2, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "utcnow", lambda: later_time)
    task_list.update()  # sin argumentos: nada cambia

    assert task_list.updated_at == creation_time

    task_list.update(name="Sprint 13")

    assert task_list.updated_at == later_time
