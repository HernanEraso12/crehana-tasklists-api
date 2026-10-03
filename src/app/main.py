"""Punto de entrada de la aplicación FastAPI."""

from fastapi import FastAPI

from app.infrastructure.api.error_handlers import register_error_handlers
from app.infrastructure.api.routers.health import router as health_router
from app.infrastructure.api.routers.invitations import router as invitations_router
from app.infrastructure.api.routers.list_tasks import router as list_tasks_router
from app.infrastructure.api.routers.task_lists import router as task_lists_router
from app.infrastructure.api.routers.task_status import router as task_status_router
from app.infrastructure.api.routers.tasks import router as tasks_router

app = FastAPI(
    title="Crehana Task Lists API",
    version="0.1.0",
)

register_error_handlers(app)
app.include_router(health_router)
app.include_router(task_lists_router)
app.include_router(list_tasks_router)
app.include_router(tasks_router)
app.include_router(task_status_router)
app.include_router(invitations_router)
