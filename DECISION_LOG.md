# Registro de decisiones técnicas

Justificación de las decisiones de arquitectura y negocio del proyecto.
Cada entrada: contexto (qué problema resuelve), decisión, alternativas
consideradas y por qué se descartaron, y consecuencias de cambiarla.
Fuente completa, decisión por decisión: [`docs/03-decisiones.md`](docs/03-decisiones.md).

## 1. Arquitectura

**Monolito modular por capas, dependencias hacia el dominio**
(A1, A2, A3, A4)

- *Contexto:* el alcance (CRUD de listas y tareas) no justifica la
  complejidad operativa de microservicios, pero el enunciado evalúa
  diseño y SOLID.
- *Decisión:* `domain` (dataclasses, sin frameworks) ← `application`
  (casos de uso) ← `infrastructure` (FastAPI, SQLAlchemy). Interfaces
  de repositorio viven en `domain`; las implementaciones concretas,
  en `infrastructure/persistence`. Python 3.12 + `uv` + `pyproject.toml`.
- *Alternativas descartadas:* microservicios (sin justificación de
  negocio para distribuir); Pydantic en todas las capas (acoplaría el
  dominio a un framework); pip + requirements.txt (sin lockfile
  reproducible).
- *Consecuencias:* cambiar esta regla implicaría que el dominio
  empezara a depender de infraestructura, perdiendo la testeabilidad
  con fakes y la posibilidad de intercambiar persistencia o extraer un
  servicio después sin tocar reglas de negocio.

**SQLAlchemy 2.0 síncrono + Alembic para migraciones** (A5, A6, A6a)

- *Contexto:* FastAPI ya ejecuta los endpoints síncronos en un
  threadpool; el esquema de BD necesita evolucionar de forma
  controlada, como en producción.
- *Decisión:* ORM síncrono (menos complejidad, sobre todo en tests);
  Alembic gestiona el esquema, la app nunca llama a `create_all()`.
  `env.py` resuelve la URL desde `Settings.DATABASE_URL` (salvo
  override explícito) y usa `render_as_batch=True` para que las
  migraciones también funcionen contra SQLite.
- *Alternativas descartadas:* SQLAlchemy async (complejidad adicional
  sin beneficio real aquí); `create_all()` (no versiona el esquema, no
  sirve para producción).
- *Consecuencias:* sin Alembic, cualquier cambio de esquema en
  producción requeriría intervención manual o perder datos.

**Código en inglés, documentación en español** (A12)

- *Contexto:* convención de la industria para identificadores; el
  evaluador y el equipo son hispanohablantes.
- *Decisión:* nombres, mensajes de error de la API y `code` en
  inglés; comentarios, docstrings y `docs/` en español.
- *Alternativas descartadas:* todo en español (menos portable si el
  código se reutiliza fuera de este contexto).
- *Consecuencias:* ninguna relevante; es una convención de estilo.

## 2. Persistencia

**PostgreSQL real + SQLite en memoria para tests** (A7)

- *Contexto:* Postgres es el stack de Crehana; correr cada test
  contra un Postgres real sería lento y agregaría una dependencia
  externa a la suite.
- *Decisión:* `docker-compose` usa PostgreSQL; los tests usan SQLite
  en memoria por defecto, con tipos genéricos para portabilidad. El
  riesgo de diferencias de dialecto se cierra con un job de CI
  (`tests-postgres`) que corre la misma suite `integration` contra un
  `postgres:16` real.
- *Alternativas descartadas:* solo SQLite (no detecta diferencias de
  dialecto); solo Postgres en tests (lento, dependencia externa para
  correr la suite localmente).
- *Consecuencias:* ver el hallazgo real que esto destapó en la
  sección 7.

**Enums como `String`; UUID como texto; fechas con `DateTime(timezone=True)`**
(A8, A13)

- *Contexto:* portabilidad entre SQLite y PostgreSQL (A7); SQLite no
  tiene tipos nativos de enum ni conserva el offset de zona horaria
  al guardar una fecha.
- *Decisión:* columnas `String` para enums y para el `id` (UUID como
  texto); `created_at`/`updated_at` con `DateTime(timezone=True)`,
  normalizadas a UTC al mapear ORM → dominio
  (`infrastructure/persistence/timestamps.as_utc`): si el valor que
  vuelve es naive, se le atribuye tzinfo UTC en vez de reinterpretar
  la hora.
- *Alternativas descartadas:* tipo `UUID`/`TIMESTAMPTZ`/`ENUM` nativos
  de Postgres (no existen igual en SQLite; forzarían dos caminos de
  código o perder los tests rápidos).
- *Consecuencias:* migrar a un Postgres-only permitiría tipos nativos,
  pero ya no se podría testear con SQLite en memoria.

**SQLite: `PRAGMA foreign_keys=ON` y `StaticPool` en tests** (A9)

- *Contexto:* SQLite no aplica claves foráneas por defecto; cada
  conexión nueva a `sqlite://` en memoria ve una base distinta.
- *Decisión:* activar el pragma en cada conexión (si no, `ON DELETE
  CASCADE` no funcionaría) y usar `StaticPool` en tests (una sola
  conexión compartida).
- *Alternativas descartadas:* ninguna razonable; sin esto, los tests
  de cascada simplemente no demuestran nada real.
- *Consecuencias:* omitir el pragma haría que la cascada de borrado
  pareciera funcionar en tests pero fallara en producción.

**Configuración centralizada con `pydantic-settings`** (A10)

- *Contexto:* la app corre en al menos tres contextos (local, tests,
  Docker), cada uno con su propia BD.
- *Decisión:* una clase `Settings` lee `DATABASE_URL` desde variables
  de entorno/`.env`; un único punto de cambio entre entornos.
- *Alternativas descartadas:* variables sueltas leídas en cada módulo
  (duplicación, sin validación de tipo).
- *Consecuencias:* agregar una variable de entorno nueva implica
  tocar un solo archivo (`infrastructure/config.py`).

## 3. Reglas de negocio

**Estados y transiciones** (B1, B2)

- *Contexto:* el enunciado pide poder cambiar el estado de una tarea,
  sin especificar una máquina de estados.
- *Decisión:* `PENDING` (inicial), `IN_PROGRESS`, `COMPLETED`.
  Cualquier transición está permitida, incluida `COMPLETED` →
  `PENDING`. Pedir el mismo estado es idempotente: no es error, pero
  tampoco toca `updated_at` (no hay un cambio real que registrar).
- *Alternativas descartadas:* una máquina de estados con transiciones
  restringidas (el enunciado no la pide; añadiría reglas inventadas).
- *Consecuencias:* si en el futuro se necesitaran transiciones
  restringidas (p. ej. no volver de `COMPLETED`), el cambio vive
  entero en `Task.change_status`, sin tocar la API ni la persistencia.

**Validación de nombre/título: obligatorio, recortado, con longitud máxima**
(B5, B6)

- *Contexto:* evitar listas/tareas sin identificación útil o con
  datos basura (espacios, textos desmedidos).
- *Decisión:* `name`/`title` obligatorios, se recortan espacios al
  inicio/fin, rechazados si quedan vacíos tras recortar o superan 100
  / 200 caracteres. La regla vive **una sola vez**, en el dominio
  (`TaskList`/`Task`); los schemas Pydantic de la API no la repiten
  (ver C9a).
- *Alternativas descartadas:* rechazar directamente un nombre con
  espacios al borde en vez de recortarlo (peor experiencia sin
  beneficio); validarlo en los schemas Pydantic (duplicaría la regla
  en dos capas, con riesgo de que diverjan).
- *Consecuencias:* cambiar el límite de caracteres es un cambio en un
  solo lugar (`domain/task_list.py` o `domain/task.py`).

**Cascada de borrado lista → tareas** (B8)

- *Contexto:* una tarea sin lista no tiene sentido.
- *Decisión:* `ON DELETE CASCADE` en la FK `tasks.list_id` (con el
  pragma de A9 activo): es la base de datos la que borra, ningún
  repositorio hace un borrado manual en Python.
- *Alternativas descartadas:* borrar las tareas manualmente desde
  `DeleteTaskList` antes de borrar la lista (código extra, y una
  carrera posible si algo más escribe en paralelo).
- *Consecuencias:* la integridad depende de la FK real; un cambio de
  motor de BD sin soporte de FK (ninguno de los usados aquí) rompería
  esto silenciosamente.

**Tarea de otra lista → 404, no revela que existe** (B9)

- *Contexto:* `GET /lists/{a}/tasks/{id-de-tarea-de-la-lista-b}` no
  debería filtrar que la tarea existe en otro lugar.
- *Decisión:* `TaskNotFoundError` se lanza tanto si la tarea no existe
  como si existe pero pertenece a otra lista; la API responde 404 en
  ambos casos, idéntico.
- *Alternativas descartadas:* 403 si existe en otra lista (revela
  información que no se pidió exponer).
- *Consecuencias:* si en el futuro se agregan permisos por usuario,
  este mismo mecanismo (ocultar existencia) se reutiliza para "no es
  tu tarea", no solo para "no es tu lista".

## 4. Contrato de la API

**PATCH parcial con sentinel `UNSET`** (C2)

- *Contexto:* un PATCH parcial necesita distinguir "no envié este
  campo" de "lo envié como `null`" (p. ej. borrar una descripción).
- *Decisión:* `UNSET` (`domain/sentinels.py`) como valor por defecto
  en `TaskList.update`/`Task.update`; los schemas de la API traducen
  esto desde `model_fields_set` de Pydantic (`exclude_unset`). Un
  body vacío es 422, no un no-op silencioso.
- *Alternativas descartadas:* usar `None` como "no enviado" (rompería
  "borrar con `null`"); aceptar un body vacío como "no cambiar nada"
  (contrato ambiguo, oculta errores del cliente).
- *Consecuencias:* cualquier campo nuevo que se agregue a un PATCH
  necesita declarar su propio default `UNSET`, siguiendo el mismo
  patrón.

**El estado solo cambia por su propio endpoint** (C3)

- *Contexto:* mezclar el cambio de estado con el PATCH general
  mezclaría dos responsabilidades en un único endpoint.
- *Decisión:* `PATCH .../status` es el único lugar que cambia el
  estado; `TaskUpdate` (el schema del PATCH general) usa
  `extra="forbid"`, así que enviar `status` ahí es 422, no se ignora
  en silencio.
- *Alternativas descartadas:* aceptar `status` en el PATCH general y
  simplemente no usarlo (confuso: el cliente cree que funcionó).
- *Consecuencias:* un cliente que dependa del comportamiento anterior
  (enviar `status` en el PATCH general) se entera con un 422 claro,
  no con un bug silencioso.

**Completitud global, calculada en SQL** (C7, C8)

- *Contexto:* el listado de tareas necesita mostrar qué porcentaje de
  la lista está completo, sin cargar todas las tareas en memoria solo
  para contarlas.
- *Decisión:* `completion_percentage` = completadas / total de **toda
  la lista**, ignorando los filtros aplicados a `items`; se calcula
  con una agregación SQL (`completion_counts`, una sola consulta) y el
  redondeo vive en una función pura de dominio
  (`domain.completion.completion_percentage`), reutilizable sin
  depender de SQL.
- *Alternativas descartadas:* calcularlo en Python cargando todas las
  tareas (no escala; el enunciado pide explícitamente no hacerlo).
- *Consecuencias:* la fórmula vive en un solo lugar; cambiarla (p. ej.
  excluir tareas archivadas del total) es un cambio en la función de
  dominio, no en cada consulta SQL.

**Formato de error único** (C9, C9a, C9b)

- *Contexto:* un cliente de la API necesita un formato de error
  predecible, sin importar si el error viene del dominio, de
  Pydantic o de un fallo no controlado.
- *Decisión:* `{"error": {"code", "message", "details"}}` para todo.
  `error_handlers.py` es el único lugar que traduce excepciones a
  HTTP. `message` siempre en inglés (coherente con los `code`); un
  error no controlado nunca expone su mensaje real ni traceback.
- *Alternativas descartadas:* dejar que FastAPI devuelva su formato
  por defecto para errores de validación (inconsistente con los
  errores de dominio).
- *Consecuencias:* agregar un nuevo tipo de excepción de dominio
  implica registrar un handler nuevo en un único archivo.

## 5. Testing y calidad

**TDD estricto, fakes en memoria, suite de contrato** (D1, D2, D3)

- *Contexto:* el enunciado evalúa testing como criterio central, no
  solo cobertura.
- *Decisión:* ciclo rojo → verde → refactor con commits separados;
  casos de uso probados con fakes en memoria, nunca mocks; la misma
  suite de contrato corre contra el fake y contra el repositorio real
  (demuestra que cumplen el mismo contrato, LSP). Markers `unit` /
  `integration`; `--cov-fail-under=75`.
- *Alternativas descartadas:* mocks en vez de fakes (acoplan el test
  a la implementación, no al comportamiento); una sola suite sin
  distinguir unit/integration (dificulta correr solo lo rápido en
  desarrollo).
- *Consecuencias:* un repositorio nuevo (p. ej. para otra entidad)
  tiene que pasar la misma suite de contrato antes de integrarse.

**`TaskStatus`/`Priority` no se testean aparte** (D8)

- *Contexto:* son `Enum` estándar de Python.
- *Decisión:* no hay tests dedicados a "un valor inválido de enum
  falla": eso ya lo garantiza el lenguaje. Se cubren implícitamente en
  los tests de `Task`/`TaskList` que usan sus valores por defecto.
- *Alternativas descartadas:* escribirlos igual, por cobertura
  artificial (no prueba nada que no pruebe ya Python).
- *Consecuencias:* ninguna; es una decisión de dónde no gastar
  esfuerzo de testing.

## 6. Entrega (Docker y CI)

**Dockerfile multistage, imagen slim, usuario no root** (D4)

- *Contexto:* la imagen de producción no debería cargar herramientas
  de build (`uv`) ni correr como root.
- *Decisión:* etapa `builder` instala dependencias con `uv` desde
  `uv.lock` (`--frozen --no-dev`); etapa final `python:3.12-slim` solo
  copia el entorno virtual y el código, corre como `appuser`, y el
  entrypoint aplica migraciones (`alembic upgrade head`) antes de
  levantar `uvicorn`.
- *Alternativas descartadas:* una sola etapa con `uv` incluido en la
  imagen final (más pesada, con herramientas de build innecesarias en
  producción).
- *Consecuencias:* cambiar una dependencia de producción no obliga a
  reinstalar herramientas de desarrollo en la imagen final.

**CI con GitHub Actions: `quality`, `tests`, `tests-postgres`, `docker`** (D5)

- *Contexto:* la vacante pide CI/CD explícitamente; además, es la
  única forma automatizada de verificar el riesgo de dialecto de A7.
- *Decisión:* cuatro jobs en cada `push`/`pull_request`. `quality`
  (lint + formato), `tests` (suite completa con cobertura),
  `tests-postgres` (la suite `integration` contra un `postgres:16`
  real vía `TEST_DATABASE_URL`), `docker` (build de la imagen, solo
  si `quality` y `tests` pasan).
- *Alternativas descartadas:* un solo job con todo (dificulta ver qué
  falló; no permite que `docker` dependa condicionalmente de los
  otros).
- *Consecuencias:* agregar un paso nuevo de verificación es agregar
  un step a un job existente o un job nuevo, sin tocar los demás.

## 7. Hallazgos durante el desarrollo

Bugs reales que el TDD y las pruebas manuales sacaron a la luz — no
hipótesis, errores que de verdad estaban en el código:

- **El fake mutaba por referencia.** `InMemoryTaskListRepository`
  guardaba la entidad que recibía tal cual; mutar el objeto devuelto
  por `get()` cambiaba silenciosamente lo "persistido" sin llamar a
  `update()`. Un test exigiendo persistencia real lo detectó.
  Solucionado guardando y devolviendo `copy.deepcopy(...)`, para que
  el fake se comporte como una BD real.
- **El reloj capturado por valor impedía controlarlo en tests.**
  `from app.domain.clock import utcnow` capturaba la función en el
  momento de importar el módulo; `monkeypatch.setattr(clock, "utcnow",
  ...)` después de eso no tenía ningún efecto sobre el valor ya
  capturado. Solucionado importando el módulo (`from app.domain import
  clock`) y llamando a `clock.utcnow()` en cada uso, para que el
  parche se vea en tiempo de ejecución.
- **`created_at` y `updated_at` distintos al crear.** Cada campo tenía
  su propio `default_factory` llamando al reloj por separado; como
  `datetime.now()` tiene resolución de microsegundos, los dos valores
  terminaban siendo distintos. Encontrado en pruebas manuales contra
  Docker. Solucionado con un sentinel: `updated_at` copia
  `created_at` si no se pasó explícitamente, así el reloj se llama
  una sola vez.
- **Transacciones abiertas que solo fallaban contra PostgreSQL real.**
  Los tests de integración creaban una sesión nueva por test y nunca
  la cerraban ni comiteaban/revertían (los repositorios hacen
  `flush()`, no `commit()`; eso lo decide la API por request). Contra
  SQLite en memoria esto era invisible, porque cada test tenía su
  propia base descartable. Contra un PostgreSQL real compartido, cada
  sesión sin cerrar dejaba una transacción `idle in transaction`
  sosteniendo locks, y el siguiente test que corría `DROP TABLE` para
  limpiar el esquema quedaba bloqueado indefinidamente. Encontrado al
  verificar a mano el job `tests-postgres` del CI. Solucionado
  cerrando sesión (con `rollback` primero) y liberando el motor
  (`dispose()`) al final de cada test de integración.

## 8. Evolución

- **Escalar a producción:** el monolito modular ya separa dominio de
  infraestructura; el siguiente paso natural sería observabilidad
  (métricas, trazas, logs estructurados) y un pool de conexiones
  dimensionado, no un cambio de arquitectura.
- **Cuándo extraer microservicios:** cuando listas y tareas tengan
  ciclos de despliegue, equipos o requisitos de escala distintos entre
  sí (p. ej. tareas con mucho más tráfico de lectura). Los límites ya
  existen como módulos (`application/create_task*.py` vs
  `*_task_list.py`); extraer un servicio sería mover ese módulo y su
  repositorio, exponiendo los mismos casos de uso detrás de una API
  nueva, sin reescribir reglas de negocio.
- **GraphQL:** se agregaría como otro adaptador en
  `infrastructure/api/` (p. ej. con Strawberry), llamando a los mismos
  casos de uso que ya usan los routers REST. El dominio y
  `application/` no cambiarían nada.
- **Despliegue serverless:** la misma app ASGI podría correr en
  AWS Lambda con un adaptador (p. ej. Mangum) envolviendo `app.main:app`,
  sin tocar dominio, casos de uso ni repositorios. La fricción real
  sería el pool de conexiones a Postgres entre invocaciones frías.

## 9. Bonus implementado

**Notificación ficticia de invitación** (E2, E3)

- *Contexto:* el enunciado ofrece notificaciones como bonus (orden E1:
  notificación → usuarios/asignación → JWT, la más barata y la que
  mejor demuestra DIP).
- *Decisión:* puerto `Notifier` en `domain` (`notify_list_invitation(list_id, email)`),
  implementado por `LoggingNotifier` en `infrastructure`, que solo
  registra la invitación en el log — no envía nada de verdad. Caso de
  uso `InviteToList` valida que la lista exista y delega en el
  notifier. Lo dispara `POST /api/v1/lists/{list_id}/invitations` con
  `{"email": EmailStr}`: 202 Accepted con `list_id` y `email`; 404
  `TASK_LIST_NOT_FOUND` si la lista no existe (sin notificar); 422 si
  el email es inválido (Pydantic `EmailStr`, dependencia nueva
  `email-validator`).
- *Alternativa descartada (E3):* disparar la notificación desde una
  asignación de responsable (`PATCH .../assignee`). Se descartó porque
  depende de la entidad `User`/`assignee`, que no existe todavía; el
  endpoint de invitación es independiente y no bloquea el resto del
  bonus.
- *Consecuencias:* reemplazar `LoggingNotifier` por un envío real
  (email, Slack, etc.) no toca `InviteToList` ni el router, solo la
  implementación de `infrastructure` y el cableado en
  `dependencies.py` (DIP).

## 10. Pendientes

### Fuera de alcance (sección F de `docs/03-decisiones.md`)

| Tema | Cómo se haría |
|---|---|
| GraphQL | adaptador en `infrastructure/api/` con Strawberry, reutilizando `application/` (ver sección 8) |
| Despliegue serverless | adaptador ASGI→Lambda (Mangum) sobre la misma app (ver sección 8) |
| Kubernetes | manifiestos (`Deployment`, `Service`, `Ingress`) a partir de la misma imagen Docker; el healthcheck de `/health` ya sirve como *liveness/readiness probe* |
| Rate limiting | middleware o gateway (p. ej. `slowapi` o un proxy como Nginx/Traefik) delante de la API, sin tocar los casos de uso |
| Caché | caché de lectura (p. ej. Redis) en los casos de uso de listado, invalidada al escribir |
| Búsqueda por texto | índice `GIN`/`tsvector` en Postgres sobre `name`/`title`, o un motor externo si crece el volumen |
| Fechas límite en tareas | un campo `due_date` opcional en `Task` (dominio) + columna nullable (migración) + filtro opcional en el listado |
| Soft delete | columna `deleted_at` nullable en vez de `DELETE`; los repositorios filtran por `deleted_at IS NULL` |
| Observabilidad (métricas/trazas) | OpenTelemetry instrumentando FastAPI y SQLAlchemy; exportando a un backend (p. ej. Prometheus/Jaeger) |
| Multi-tenancy | columna `owner_id`/`tenant_id` en `TaskList`, con el alcance de unicidad de nombre pasando a ser por propietario (ver B7) |

### Bonus no implementado (sección E, orden E1: notificación → usuarios/asignación → JWT)

| Bonus | Cómo se haría |
|---|---|
| Usuarios + asignación de responsable | entidad `User` en el dominio, campo `assignee_id` opcional en `Task`, caso de uso `AssignTask` que reutiliza el puerto `Notifier` ya implementado (ver sección 9) |
| JWT | capa de autenticación (`/auth/register`, `/auth/login`) y un `Depends` que proteja todos los endpoints salvo `/health`, `/auth/*` y `/docs` (E4) |
