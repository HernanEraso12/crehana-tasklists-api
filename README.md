# Crehana Task Lists API

API REST de listas de tareas (prueba técnica Backend — Crehana). Permite
crear listas, agregar tareas dentro de ellas, cambiar su estado y
consultarlas con filtros, paginación y porcentaje de completitud.

Decisiones de negocio y técnicas completas en
[`docs/03-decisiones.md`](docs/03-decisiones.md).

## Arquitectura

Monolito modular por capas. **Las dependencias apuntan siempre hacia el
dominio**, nunca al revés:

```
┌─────────────────────────────────────────────┐
│ infrastructure                               │
│  ├── api/            (FastAPI, Pydantic)     │
│  └── persistence/    (SQLAlchemy, Alembic)   │
│              │                               │
│              ▼                               │
│       application     (casos de uso)         │
│              │                               │
│              ▼                               │
│         domain        (entidades, reglas)    │
└─────────────────────────────────────────────┘
```

- **`domain/`**: entidades (`dataclasses`), enums, excepciones e
  interfaces de repositorio. No importa FastAPI, Pydantic ni SQLAlchemy.
- **`application/`**: casos de uso. Solo importa de `domain/`.
- **`infrastructure/`**: adaptadores — `api/` (routers, schemas,
  manejo de errores, composition root) y `persistence/` (modelos ORM,
  repositorios concretos, migraciones).

Los endpoints no tienen lógica de negocio: cada uno llama a un caso de
uso. Las excepciones de dominio no conocen HTTP; `error_handlers.py` es
el único lugar que las traduce a códigos.

## Stack

| Herramienta | Por qué |
|---|---|
| Python 3.12 | versión estable más reciente al iniciar el proyecto |
| FastAPI | tipado, validación y documentación OpenAPI integradas |
| Pydantic v2 | validación de la capa API, separada del dominio |
| SQLAlchemy 2.0 (síncrono) | ORM tipado; síncrono porque FastAPI ya corre los endpoints en threadpool y simplifica los tests |
| Alembic | migraciones de esquema controladas, sin `create_all()` en la app |
| PostgreSQL | base de datos real, alineada al stack de Crehana |
| SQLite (en memoria) | tests rápidos y sin dependencias externas |
| `uv` | gestor de dependencias y entornos, con lockfile reproducible |
| pytest + pytest-cov | tests y cobertura |
| flake8 + black + isort | linter y formateo, pedidos por el enunciado |
| Docker / docker-compose | ejecución reproducible, con PostgreSQL real |

## Requisitos previos

- [Python 3.12](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias)
- [Docker](https://www.docker.com/) y Docker Compose (solo si se quiere
  correr con PostgreSQL en contenedores)

## Configuración

Copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

Variables (ver [`.env.example`](.env.example)):

| Variable | Para qué |
|---|---|
| `DATABASE_URL` | URL de conexión que usa la app (y Alembic). Por defecto, SQLite local (`sqlite:///./local.db`); la línea de PostgreSQL está comentada, para usarse al correr fuera de Docker contra un Postgres propio |
| `LOG_LEVEL` | nivel del logger `app` (p. ej. `LoggingNotifier`, bonus E2). Por defecto `INFO`; se ve en stdout junto a los logs de uvicorn (ver [`DECISION_LOG.md`](DECISION_LOG.md), sección 7) |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | credenciales del servicio `db` de `docker-compose.yml`. Son valores por defecto **solo para desarrollo**; `docker-compose` construye `DATABASE_URL` del contenedor `app` a partir de estas tres, no hace falta repetirla |

## Ejecución local (SQLite, sin Docker)

```bash
uv sync                               # instala dependencias
uv run alembic upgrade head           # crea el esquema (SQLite local)
uv run uvicorn app.main:app --reload  # levanta la API en :8000
```

Swagger UI: http://localhost:8000/docs · Healthcheck: http://localhost:8000/health

## Ejecución con Docker (PostgreSQL)

```bash
cp .env.example .env            # si no existe ya
docker compose up --build       # construye la imagen y levanta app + db
```

`app` espera a que `db` esté sano (`depends_on: condition: service_healthy`)
y corre `alembic upgrade head` antes de arrancar `uvicorn` (ver
[`docker-entrypoint.sh`](docker-entrypoint.sh)). Mismas URLs que en local:
http://localhost:8000/docs y http://localhost:8000/health.

Apagar y limpiar (incluido el volumen de Postgres):

```bash
docker compose down -v
```

## Tests

```bash
uv run pytest                 # suite completa (unit + integration), con cobertura
uv run pytest -m unit         # solo unitarios (dominio y casos de uso, con fakes)
uv run pytest -m integration  # solo integración (persistencia y API), SQLite en memoria
```

### Contra PostgreSQL real

Los fixtures de integración usan la variable `TEST_DATABASE_URL` si está
definida, y SQLite en memoria si no (en local, sin la variable, nada
cambia). Para correrlos contra el PostgreSQL de `docker-compose` (en una
base separada de la de la app, para no pisar datos):

```bash
docker compose up -d db
docker compose exec db psql -U crehana -d crehana_tasklists \
  -c "CREATE DATABASE crehana_tasklists_test;"

TEST_DATABASE_URL="postgresql+psycopg://crehana:crehana@localhost:5432/crehana_tasklists_test" \
  uv run pytest -m integration
```

Así es exactamente como corre el job `tests-postgres` del CI, contra un
`postgres:16` efímero.

## Cobertura

`pytest.ini` define `--cov-fail-under=75`: la suite falla si la
cobertura total baja de 75 %. Cobertura actual, muy por encima del
umbral (98 %+).

## Linter y formato

```bash
uv run flake8                                          # linter (.flake8: max-line-length=88)
uv run black --check . && uv run isort --check-only .  # formato (sin aplicar)
```

Atajos del `Makefile` (requiere **GNU make**: Linux, macOS o WSL en
Windows; `make` no viene instalado por defecto en Windows/Git Bash):

```bash
make install   # uv sync
make test      # uv run pytest
make lint      # uv run flake8
make format    # aplica black + isort
make up        # docker compose up --build
```

## API

Documentación interactiva (Swagger): http://localhost:8000/docs

Incluye el bonus de notificación ficticia (E2/E3): `POST
/api/v1/lists/{list_id}/invitations` invita por email a colaborar en
una lista. Responde 202 y dispara un puerto `Notifier` (`LoggingNotifier`)
que solo registra la invitación en el log, sin enviar nada de verdad —
pensado para ser reemplazado por un envío real (email, Slack, etc.)
sin tocar el caso de uso.

Contrato completo, payloads y formato de error en
[`docs/04-api.md`](docs/04-api.md). Resumen:

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/lists` | Crear lista |
| `GET` | `/api/v1/lists` | Listar listas (paginado) |
| `GET` | `/api/v1/lists/{list_id}` | Obtener lista |
| `PATCH` | `/api/v1/lists/{list_id}` | Actualizar lista (parcial) |
| `DELETE` | `/api/v1/lists/{list_id}` | Eliminar lista (cascada a sus tareas) |
| `POST` | `/api/v1/lists/{list_id}/tasks` | Crear tarea |
| `GET` | `/api/v1/lists/{list_id}/tasks` | Listar tareas (filtros + completitud) |
| `GET` | `/api/v1/lists/{list_id}/tasks/{task_id}` | Obtener tarea |
| `PATCH` | `/api/v1/lists/{list_id}/tasks/{task_id}` | Actualizar tarea (sin estado) |
| `PATCH` | `/api/v1/lists/{list_id}/tasks/{task_id}/status` | Cambiar estado |
| `DELETE` | `/api/v1/lists/{list_id}/tasks/{task_id}` | Eliminar tarea |
| `POST` | `/api/v1/lists/{list_id}/invitations` | Invitar por email a colaborar en la lista (bonus, notificación ficticia) |
| `GET` | `/health` | Healthcheck (verifica conexión a la BD) |

## CI (GitHub Actions)

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) corre en cada
`push` y `pull_request`, con cuatro jobs:

| Job | Qué hace |
|---|---|
| `quality` | `flake8`, `black --check`, `isort --check-only` |
| `tests` | suite completa de `pytest`, con cobertura (falla bajo 75 %) |
| `tests-postgres` | levanta un servicio `postgres:16` y corre los tests `integration` contra él (`TEST_DATABASE_URL`), para detectar diferencias de dialecto con SQLite |
| `docker` | construye la imagen con el `Dockerfile` (sin publicarla); solo corre si `quality` y `tests` pasan |

## Estructura de carpetas

```
src/app/
  domain/            # entidades, enums, excepciones, interfaces de repositorio
  application/       # casos de uso
  infrastructure/
    api/             # routers, schemas, manejo de errores, composition root
    persistence/     # modelos ORM, repositorios, sesión, config de Alembic
  main.py
tests/
  unit/domain/              # reglas de negocio puras
  unit/application/         # casos de uso con repositorios fake en memoria
  integration/persistence/  # tests de contrato contra BD real
  integration/api/          # TestClient end-to-end
docs/                       # requerimientos, decisiones, contrato de API, plan TDD
alembic/                    # migraciones
```

## Decisiones técnicas

Justificación de cada decisión de arquitectura y negocio (qué problema
resuelve, por qué esa opción y no otra) en
[`DECISION_LOG.md`](DECISION_LOG.md).
