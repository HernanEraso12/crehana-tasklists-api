"""Cálculo de completitud como función pura de dominio (C8):
completion_percentage(completed, total) -> float, 2 decimales, 0.0 si
la lista no tiene tareas. Rechaza conteos inválidos."""

import pytest

from app.domain.completion import completion_percentage
from app.domain.exceptions import InvalidCompletionCountsError

pytestmark = pytest.mark.unit


def test_zero_tasks_returns_zero() -> None:
    assert completion_percentage(completed=0, total=0) == 0.0


def test_zero_completed_of_three_returns_zero() -> None:
    assert completion_percentage(completed=0, total=3) == 0.0


def test_one_of_three_returns_33_33() -> None:
    assert completion_percentage(completed=1, total=3) == 33.33


def test_two_of_three_returns_66_67() -> None:
    assert completion_percentage(completed=2, total=3) == 66.67


def test_three_of_three_returns_100() -> None:
    assert completion_percentage(completed=3, total=3) == 100.0


def test_rejects_negative_completed() -> None:
    with pytest.raises(InvalidCompletionCountsError):
        completion_percentage(completed=-1, total=3)


def test_rejects_negative_total() -> None:
    with pytest.raises(InvalidCompletionCountsError):
        completion_percentage(completed=0, total=-1)


def test_rejects_completed_greater_than_total() -> None:
    with pytest.raises(InvalidCompletionCountsError):
        completion_percentage(completed=4, total=3)
