"""Reloj del dominio. Punto único para obtener la hora actual en UTC (B10)."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
