"""Enums de dominio: estados de tarea (B1) y prioridades (B3).

Son `Enum` estándar de Python: un valor fuera del conjunto permitido ya
es rechazado por el lenguaje (`ValueError`), sin lógica adicional que
implementar ni testear más allá de documentar los valores esperados.
"""

from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
