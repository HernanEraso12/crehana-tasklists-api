# Plan de implementación con TDD

Cada ítem es un ciclo rojo → verde → refactor con sus commits. Marcar al completar.

## Fase 0 — Esqueleto (sin lógica, un solo commit `chore:`)

- [x] Estructura de carpetas, `pyproject.toml` con `uv`, `pytest.ini`, `.flake8`, config de black/isort
- [x] `.gitignore`, `.env.example`, `Makefile`
- [x] Un test trivial que pase para validar que pytest y la cobertura funcionan

## Fase 1 — Dominio (`tests/unit/domain`)

- [x] `TaskStatus` y `Priority` solo aceptan valores válidos
- [x] Crear `TaskList` con nombre válido; rechaza vacío, solo espacios y > 100 caracteres
- [x] Crear `Task` con estado inicial `PENDING` y prioridad por defecto `MEDIUM`
- [x] `Task` rechaza título vacío o > 200 caracteres
- [x] `task.change_status(...)` permite cualquier transición y actualiza `updated_at`
- [x] Cálculo de completitud: 0 tareas → 0.0; 0 de 3 → 0.0; 1 de 3 → 33.33; 3 de 3 → 100.0

## Fase 2 — Casos de uso de listas (`tests/unit/application`, con fakes)

- [x] Crear lista
- [x] Obtener lista existente / inexistente → `TaskListNotFoundError`
- [x] Listar listas con paginación
- [x] Actualizar lista (parcial) / inexistente
- [x] Eliminar lista / inexistente

## Fase 3 — Casos de uso de tareas

- [x] Crear tarea en lista existente / en lista inexistente → `TaskListNotFoundError`
- [x] Obtener tarea / inexistente / de otra lista → `TaskNotFoundError`
- [x] Actualizar tarea (sin tocar estado)
- [x] Eliminar tarea
- [x] Cambiar estado (incluye `COMPLETED` → `PENDING` e idempotencia)

## Fase 4 — Listado con filtros y completitud

- [x] Filtrar por estado, por prioridad y combinados
- [x] `total` refleja el filtro; `completion_percentage` es global (ignora los filtros)
- [x] La completitud cambia al completar, reabrir y eliminar tareas

## Fase 5 — Persistencia (`tests/integration/persistence`)

- [x] Suite de contrato parametrizada: misma batería contra fake y repositorio SQLAlchemy
- [x] Borrado en cascada lista → tareas
- [x] Completitud calculada con agregación SQL (`completion_counts`)
- [x] Migración inicial de Alembic

## Fase 6 — API (`tests/integration/api`, `TestClient` + SQLite)

- [x] CRUD de listas: códigos 201/200/204/404/422 y header `Location`
- [x] CRUD de tareas, incluido el 404 de tarea en otra lista
- [x] `PATCH .../status`
- [x] Listado filtrado con completitud
- [ ] Formato de error único (404 y 422)
- [ ] UUID inválido → 422
- [ ] `/health`

## Fase 7 — Entrega

- [ ] Dockerfile multistage + `docker-compose.yml` con PostgreSQL; probar `docker compose up` desde cero
- [ ] GitHub Actions
- [ ] `README.md`
- [ ] `DECISION_LOG.md` (a partir de `docs/03-decisiones.md`) con sección de pendientes
- [ ] Verificar cobertura ≥ 75%, flake8, black e isort en limpio

## Fase 8 — Bonus (solo si sobra tiempo)

- [ ] Notificación ficticia (`Notifier` + `LoggingNotifier`)
- [ ] Usuarios + asignación de responsable
- [ ] JWT
