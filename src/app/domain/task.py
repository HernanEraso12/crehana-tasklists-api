"""Entidad de dominio Task (B1, B3, B6)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.enums import Priority, TaskStatus


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Task:
    title: str
    list_id: UUID
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
