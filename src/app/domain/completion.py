"""Cálculo del porcentaje de completitud de una lista (C8)."""

from app.domain.exceptions import InvalidCompletionCountsError


def completion_percentage(completed: int, total: int) -> float:
    if completed < 0 or total < 0:
        raise InvalidCompletionCountsError("completed and total cannot be negative.")
    if completed > total:
        raise InvalidCompletionCountsError("completed cannot be greater than total.")
    if total == 0:
        return 0.0
    return round(completed / total * 100, 2)
