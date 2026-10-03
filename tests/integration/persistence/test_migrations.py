"""Migración inicial de Alembic (A6): el esquema se gestiona con
Alembic, no con `create_all()` en la app. Verifica que
`alembic upgrade head` deja un esquema utilizable (incluida la cascada
`ON DELETE CASCADE`, B8) y que no hay diferencias entre los modelos
ORM y las migraciones (equivalente a `alembic check`, vía
`compare_metadata`)."""

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from alembic.autogenerate import compare_metadata
from alembic.command import upgrade
from alembic.config import Config
from alembic.migration import MigrationContext
from app.domain.task import Task
from app.domain.task_list import TaskList
from app.infrastructure.persistence.database import Base, create_sqlalchemy_engine
from app.infrastructure.persistence.sqlalchemy_task_list_repository import (
    SqlAlchemyTaskListRepository,
)
from app.infrastructure.persistence.sqlalchemy_task_repository import (
    SqlAlchemyTaskRepository,
)

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _alembic_config_for(database_url: str) -> Config:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@pytest.fixture
def migrated_database_url(tmp_path: Path) -> str:
    """Aplica 'alembic upgrade head' sobre un SQLite temporal y
    devuelve su URL, lista para usarse."""
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    upgrade(_alembic_config_for(database_url), "head")
    return database_url


def test_migration_creates_a_schema_with_cascade_delete(
    migrated_database_url: str,
) -> None:
    engine = create_sqlalchemy_engine(migrated_database_url)
    session = Session(engine)
    task_list_repository = SqlAlchemyTaskListRepository(session)
    task_repository = SqlAlchemyTaskRepository(session)
    task_list = TaskList(name="Sprint 12")
    task_list_repository.add(task_list)
    task = Task(title="Escribir tests", list_id=task_list.id)
    task_repository.add(task)

    task_list_repository.delete(task_list.id)

    assert task_repository.get(task.id) is None


def test_models_match_migrations(migrated_database_url: str) -> None:
    engine = create_sqlalchemy_engine(migrated_database_url)
    with engine.connect() as connection:
        migration_context = MigrationContext.configure(connection)
        diff = compare_metadata(migration_context, Base.metadata)

    assert diff == []
