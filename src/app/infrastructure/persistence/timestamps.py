"""Normalización de fechas leídas de la BD (A13)."""

from datetime import datetime, timezone


def as_utc(value: datetime) -> datetime:
    """SQLite no conserva el offset de zona horaria: lo que vuelve es
    naive pero representa la misma hora UTC que se guardó. Si ya trae
    tzinfo (p. ej. Postgres), se normaliza a UTC en vez de asumir."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
