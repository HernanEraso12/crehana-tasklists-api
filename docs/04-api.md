# Contrato de la API

Base: `/api/v1`. Documentación interactiva en `/docs` (Swagger) y `/redoc`.

## Endpoints

| Método | Ruta | Descripción | Éxito | Errores |
|---|---|---|---|---|
| POST | `/lists` | Crear lista | 201 + `Location` | 422 |
| GET | `/lists?limit=&offset=` | Listar listas | 200 | 422 |
| GET | `/lists/{list_id}` | Obtener lista | 200 | 404, 422 |
| PATCH | `/lists/{list_id}` | Actualizar lista | 200 | 404, 422 |
| DELETE | `/lists/{list_id}` | Eliminar lista y sus tareas | 204 | 404 |
| POST | `/lists/{list_id}/tasks` | Crear tarea | 201 + `Location` | 404, 422 |
| GET | `/lists/{list_id}/tasks?status=&priority=&limit=&offset=` | Listar tareas + completitud | 200 | 404, 422 |
| GET | `/lists/{list_id}/tasks/{task_id}` | Obtener tarea | 200 | 404, 422 |
| PATCH | `/lists/{list_id}/tasks/{task_id}` | Actualizar tarea (sin estado) | 200 | 404, 422 |
| PATCH | `/lists/{list_id}/tasks/{task_id}/status` | Cambiar estado | 200 | 404, 422 |
| DELETE | `/lists/{list_id}/tasks/{task_id}` | Eliminar tarea | 204 | 404 |
| POST | `/lists/{list_id}/invitations` | Invitar por email a colaborar en la lista (bonus E2/E3, notificación ficticia) | 202 | 404, 422 |
| GET | `/health` (sin prefijo) | Healthcheck con BD | 200 | 503 |

422 en rutas con ID: UUID mal formado.

## Payloads

### Lista

```jsonc
// POST /lists
{ "name": "Sprint 12", "description": "Opcional" }

// PATCH /lists/{id}  — al menos un campo
{ "name": "Sprint 12 (v2)" }

// Respuesta
{
  "id": "uuid",
  "name": "Sprint 12",
  "description": "Opcional",
  "created_at": "2026-10-02T15:00:00Z",
  "updated_at": "2026-10-02T15:00:00Z"
}
```

### Tarea

```jsonc
// POST /lists/{id}/tasks
{ "title": "Escribir tests", "description": "Opcional", "priority": "HIGH" }  // priority por defecto MEDIUM

// PATCH /lists/{id}/tasks/{task_id}  — title, description, priority; no status
{ "priority": "LOW" }

// PATCH /lists/{id}/tasks/{task_id}/status
{ "status": "COMPLETED" }

// Respuesta
{
  "id": "uuid",
  "list_id": "uuid",
  "title": "Escribir tests",
  "description": null,
  "priority": "HIGH",
  "status": "PENDING",
  "created_at": "...",
  "updated_at": "..."
}
```

### Listados

```jsonc
// GET /lists
{ "items": [ /* listas */ ], "total": 3, "limit": 20, "offset": 0 }

// GET /lists/{id}/tasks?status=PENDING&priority=HIGH
{
  "items": [ /* tareas filtradas */ ],
  "total": 2,                    // total filtrado
  "limit": 20,
  "offset": 0,
  "completion_percentage": 33.33 // global de la lista, ignora filtros
}
```

### Invitación a una lista (bonus)

```jsonc
// POST /lists/{id}/invitations
{ "email": "colega@example.com" }

// Respuesta (202 Accepted)
{ "list_id": "uuid", "email": "colega@example.com" }
```

No persiste nada ni cambia el estado de la lista: dispara el puerto
`Notifier` (`LoggingNotifier`, E2), que solo registra la invitación en
el log. `email` inválido → 422; lista inexistente → 404
`TASK_LIST_NOT_FOUND` (y no se notifica).

## Formato de error

```json
{
  "error": {
    "code": "TASK_LIST_NOT_FOUND",
    "message": "Task list 3f2c... not found",
    "details": null
  }
}
```

| Excepción (dominio/aplicación) | HTTP | `code` |
|---|---|---|
| `TaskListNotFoundError` | 404 | `TASK_LIST_NOT_FOUND` |
| `TaskNotFoundError` (incluye tarea de otra lista) | 404 | `TASK_NOT_FOUND` |
| `InvalidTaskListError` / `InvalidTaskError` (regla de dominio) | 422 | `VALIDATION_ERROR` |
| Validación Pydantic (`RequestValidationError`) | 422 | `VALIDATION_ERROR` (con `details`) |
| Error no controlado | 500 | `INTERNAL_ERROR` (sin detalles internos) |
| `OperationalError` de SQLAlchemy (BD no disponible) | 503 | `SERVICE_UNAVAILABLE` |

## Bonus pendiente (si hay tiempo)

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/register` | Registrar usuario |
| POST | `/auth/login` | Obtener JWT |
| PATCH | `/lists/{list_id}/tasks/{task_id}/assignee` | Asignar responsable; dispara la misma notificación ficticia (E2) que `/invitations` |
