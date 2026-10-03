"""Parámetros de paginación compartidos entre listados (C5): `limit`
(defecto 20, máx. 100) y `offset` (defecto 0, no negativo). El default
se da en el parámetro de cada endpoint (`= 20`, `= 0`); aquí solo
viven las restricciones."""

from typing import Annotated

from fastapi import Query

LimitQuery = Annotated[int, Query(ge=1, le=100)]
OffsetQuery = Annotated[int, Query(ge=0)]
