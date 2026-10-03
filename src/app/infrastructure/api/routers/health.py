"""Healthcheck (C12). Sin prefijo `/api/v1`: verifica la conexión a la
base de datos con una consulta real (`SELECT 1`), no solo responde
"ok" sin tocarla. Si la BD no responde, `OperationalError` se mapea a
503 en `error_handlers.py` (no hay try/except aquí: ese es el único
lugar que traduce excepciones a HTTP, `CLAUDE.md`)."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.api.dependencies import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: Session = Depends(get_db_session)) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "ok"}
