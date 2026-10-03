# Decisiones del proyecto

> Fuente para el `DECISION_LOG.md` final. Cada decisión responde: qué problema resuelve, por qué esta
> opción y no otra, y qué implicaría cambiarla.
> Estado: **Tomada** = aplicar. **Por confirmar** = proponer, no implementar sin confirmación.

## A. Arquitectura y stack

| # | Decisión | Alternativa descartada | Por qué | Estado |
|---|---|---|---|---|
| A1 | Monolito modular por capas (domain / application / infrastructure) | Microservicios | El alcance no justifica distribución; los límites internos permiten extraer servicios después | Tomada |
| A2 | Dependencias hacia el dominio; interfaces de repositorio en `domain` | Repos concretos usados directamente en casos de uso | DIP: casos de uso testeables con fakes; persistencia intercambiable | Tomada |
| A3 | Entidades de dominio como `dataclasses`; Pydantic solo en la API | Pydantic en todas las capas | El dominio no depende de frameworks | Tomada |
| A4 | Python 3.12 + `uv` + `pyproject.toml` | pip + requirements.txt | Herramientas modernas (criterio evaluado), lockfile reproducible | Tomada |
| A5 | SQLAlchemy 2.0 **síncrono** | SQLAlchemy async | Menos complejidad, sobre todo en tests; FastAPI ejecuta endpoints síncronos en threadpool | Tomada |
| A6 | Alembic para migraciones | `create_all()` | Evolución de esquema controlada, como en producción | Tomada |
| A6a | `alembic/env.py`: `target_metadata = Base.metadata`, `render_as_batch=True` (SQLite no soporta `ALTER TABLE` directo), URL desde `Settings.DATABASE_URL` salvo que `alembic.ini` (`sqlalchemy.url`, vacío por defecto) o un `config.set_main_option(...)` la sobrescriban; usa el mismo `create_sqlalchemy_engine` que la app, para que el `PRAGMA foreign_keys=ON` de SQLite (A9) también aplique al migrar | Tomada |
| A7 | **PostgreSQL** en docker-compose; **SQLite en memoria** para tests | Solo SQLite / solo PostgreSQL | Postgres alineado al stack de Crehana; SQLite hace los tests rápidos y sin dependencias. Riesgo de diferencias de dialecto mitigado con tipos genéricos y un job de CI opcional contra Postgres | Tomada |
| A8 | Enums guardados como `String`, no tipo nativo | Enum nativo de Postgres | Portabilidad entre SQLite y Postgres; migraciones simples | Tomada |
| A9 | SQLite: `PRAGMA foreign_keys=ON` por conexión y `StaticPool` en tests | — | Sin el pragma no hay integridad ni cascada; sin `StaticPool` cada conexión ve otra BD | Tomada |
| A10 | Configuración con `pydantic-settings` y `DATABASE_URL` | Variables sueltas | Un único punto de cambio de BD entre entornos | Tomada |
| A11 | flake8 + black + isort (`profile=black`) | ruff | Lo pide el enunciado explícitamente; ruff se menciona como alternativa futura que unificaría flake8 + isort | Tomada |
| A12 | Código en inglés, documentación en español | Todo en español | Convención de la industria; el evaluador es hispanohablante | Tomada |
| A13 | Modelos ORM: `id` como `String(36)` (UUID como texto), fechas con `DateTime(timezone=True)`; los repositorios normalizan a UTC al mapear ORM→dominio con `infrastructure/persistence/timestamps.as_utc` (compartido entre `SqlAlchemyTaskListRepository` y `SqlAlchemyTaskRepository`: atribuye tzinfo UTC a un valor naive en vez de reinterpretar la hora) | Tipo nativo `UUID`/`TIMESTAMPTZ` de Postgres | Portabilidad SQLite/Postgres (A7, A8); SQLite no conserva el offset de zona horaria al guardar, así que hay que reatribuirlo al leer, no reconvertir | Tomada |

## B. Reglas de negocio

| # | Decisión | Estado |
|---|---|---|
| B1 | Estados: `PENDING`, `IN_PROGRESS`, `COMPLETED`. Estado inicial: `PENDING` | Tomada |
| B2 | **Cualquier transición está permitida**, incluida volver de `COMPLETED` a `PENDING`. Cambiar al mismo estado es idempotente (200) **y no modifica `updated_at`** (no hay cambio real que registrar). No se inventa una máquina de estados que el enunciado no pide | Tomada |
| B3 | Prioridades: `LOW`, `MEDIUM`, `HIGH`. Por defecto: `MEDIUM` | Tomada |
| B4 | IDs: UUID v4 | Tomada |
| B5 | Lista: `name` obligatorio (1-100 caracteres tras recortar espacios al inicio/fin, no vacío), `description` opcional (≤ 500) | Tomada |
| B6 | Tarea: `title` obligatorio (1-200, recortado, no vacío), `description` opcional (≤ 1000), `priority`, `status`. **No se incluye fecha límite** (fuera de alcance, documentado como pendiente) | Tomada |
| B7 | Nombres de lista **no son únicos**. Sin usuarios no hay un ámbito razonable de unicidad; con usuarios sería único por propietario | Tomada |
| B8 | Eliminar una lista elimina sus tareas (cascada), implementado con `ON DELETE CASCADE` en la FK `tasks.list_id` (con `PRAGMA foreign_keys=ON`, A9) — es la base de datos la que borra, ningún repositorio hace un borrado manual de tareas en Python | Tomada |
| B9 | Una tarea consultada bajo una lista que no es la suya → **404** (no se revela que existe en otra lista) | Tomada |
| B10 | `created_at` y `updated_at` en UTC, gestionados por la aplicación | Tomada |

## C. Contrato de la API

| # | Decisión | Estado |
|---|---|---|
| C1 | Prefijo de versión `/api/v1` | Tomada |
| C2 | Actualizaciones con **PATCH parcial**. Body sin campos → 422. El dominio y los casos de uso distinguen "campo no enviado" de "campo enviado como `null`" con un sentinel `UNSET` (`app.domain.sentinels`): `description=None` la borra, no enviarla la conserva. La capa API (Fase 6) traduce esto desde `model_fields_set` de Pydantic | Tomada |
| C3 | El estado **no** se cambia por el PATCH general: solo por `PATCH .../status`. Un caso de uso, un endpoint (SRP) | Tomada |
| C4 | Filtros `status` y `priority` opcionales y **combinables** (AND), un valor cada uno | Tomada |
| C5 | Paginación `limit` (defecto 20, máx. 100) y `offset` en listados | Tomada |
| C6 | Orden por `created_at` ascendente | Tomada |
| C7 | Respuesta del listado de tareas: `items`, `total` (filtrado), `limit`, `offset`, `completion_percentage` | Tomada |
| C8 | `completion_percentage` = completadas / totales × 100 sobre **toda la lista, sin filtros**; float con 2 decimales; **0.0** si la lista no tiene tareas; calculado con agregación SQL, no cargando tareas en memoria. La fórmula y el redondeo viven en `domain.completion.completion_percentage(completed, total)`, una función pura; la agregación SQL (Fase 5) solo obtiene los conteos y delega el cálculo a esta función | Tomada |
| C9 | Formato de error único: `{"error": {"code", "message", "details"}}`, incluyendo los 422 de validación | Tomada |
| C10 | 201 incluye header `Location` con la URL del recurso creado | Tomada |
| C11 | Sin HATEOAS completo: OpenAPI cubre el descubrimiento. Links solo en `Location` | Tomada |
| C12 | `GET /health` verifica conexión a BD (200 / 503) | Tomada |
| C13 | 409 queda reservado; en el alcance obligatorio no hay conflictos de negocio (ver B7) | Tomada |

## D. Calidad y entrega

| # | Decisión | Estado |
|---|---|---|
| D1 | TDD con commits separados `test:` → `feat:` → `refactor:` | Tomada |
| D2 | Fakes en memoria para casos de uso; misma suite de contrato contra fake y SQLAlchemy (demuestra LSP) | Tomada |
| D3 | Markers `unit` / `integration`; `--cov-fail-under=75` en `pytest.ini` | Tomada |
| D4 | Dockerfile multistage, imagen slim, usuario no root, migraciones al arrancar el contenedor | Tomada |
| D8 | No se testean `TaskStatus`/`Priority` por separado: son `Enum` estándar de Python, la validación de valores la da el lenguaje. Se cubren implícitamente en los tests de `Task`/`TaskList` que usan sus defaults | Tomada |
| D5 | **CI con GitHub Actions** (lint, format check, tests, build). Sube de prioridad porque la vacante pide CI/CD explícitamente | Tomada |
| D6 | `Makefile` con `test`, `lint`, `format`, `up` | Tomada |
| D7 | No subir `.claude/` ni `CLAUDE.md` al repositorio (por ahora); se excluyen vía `.gitignore` | Tomada |

## E. Bonus (solo tras completar lo obligatorio)

| # | Decisión | Estado |
|---|---|---|
| E1 | Orden: notificación ficticia → usuarios + asignación → JWT. La notificación es la más barata y mejor demuestra DIP | Tomada |
| E2 | Puerto `Notifier` en `domain`/`application`; implementación `LoggingNotifier` que solo registra en log | Tomada |
| E3 | **Qué dispara la "invitación":** (a) asignar una tarea notifica al responsable, o (b) `POST /lists/{id}/invitations` con un email invita a colaborar en la lista | **Por confirmar** (recomendado: a, reutiliza la asignación) |
| E4 | Si hay JWT: proteger todo excepto `/health`, `/auth/*` y `/docs` | Tomada |

## F. Fuera de alcance (va a la sección "Pendientes" del DECISION_LOG)

GraphQL, despliegue serverless, Kubernetes, rate limiting, caché, búsqueda por texto, fechas límite,
soft delete, observabilidad (métricas/trazas), multi-tenancy. Para cada uno, una línea de cómo se haría.
