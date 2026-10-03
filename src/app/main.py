"""Punto de entrada de la aplicación FastAPI."""

from fastapi import FastAPI

from app.infrastructure.api.error_handlers import register_error_handlers
from app.infrastructure.api.routers.task_lists import router as task_lists_router

app = FastAPI(
    title="Crehana Task Lists API",
    version="0.1.0",
)

register_error_handlers(app)
app.include_router(task_lists_router)
