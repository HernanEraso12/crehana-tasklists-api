from logging.config import fileConfig

from alembic import context
from app.infrastructure.config import Settings
from app.infrastructure.persistence.database import Base, create_sqlalchemy_engine

# Importan los modelos para que se registren en Base.metadata; no se
# usan directamente, pero sin este import target_metadata quedaría
# vacío (noqa: F401, import "solo por el efecto secundario").
from app.infrastructure.persistence.models import (  # noqa: F401,E501
    TaskListModel,
    TaskModel,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# disable_existing_loggers=False (default True): alembic.command.upgrade
# puede correr en el mismo proceso que la app o la suite de tests
# (test_migrations.py); con el default, fileConfig deshabilita
# permanentemente cualquier logger ya creado (p. ej. "app",
# configurado por app.infrastructure.logging_config) que no esté
# listado en alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Los modelos ORM son la fuente de verdad para autogenerate.
target_metadata = Base.metadata


def get_url() -> str:
    """La URL viene de Settings.DATABASE_URL (A10). Un test puede
    sobrescribirla llamando a config.set_main_option("sqlalchemy.url",
    ...) antes de correr la migración, sin tocar variables de entorno."""
    url = config.get_main_option("sqlalchemy.url")
    return url or Settings().database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Usa el mismo factory de motor que la app (`create_sqlalchemy_engine`):
    así las migraciones también corren con PRAGMA foreign_keys=ON
    cuando la BD es SQLite (A9).
    """
    connectable = create_sqlalchemy_engine(get_url())

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # render_as_batch=True (SQLite no soporta ALTER TABLE
            # directo; Alembic recrea la tabla en un "batch").
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
