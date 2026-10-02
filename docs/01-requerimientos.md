# Requerimientos oficiales de la prueba

> Enunciado entregado por Crehana. Es la fuente de verdad del alcance.

## Qué evalúa

- Diseño de API REST y estructura limpia de código.
- Uso de herramientas modernas de desarrollo en Python.
- Pensamiento técnico y capacidad de justificación.
- Buenas prácticas: testing, Docker, linters, validaciones.
- Tiempo estimado: 4-6 horas. Si no se cubre todo, priorizar lo principal y **documentar lo que quedaría pendiente**.

## Requisitos técnicos

- Lenguaje: Python
- Framework de API: FastAPI
- Base de datos: una base de datos real a elección.
- Pruebas: pytest o unittest
- Linter: flake8 o pylint
- Formateo: black
- Docker: contenedor para ejecutar la aplicación.

## 1. Casos de uso

### a. Básicos (obligatorios)

1. Crear, obtener, actualizar y eliminar listas de tareas.
2. Crear, obtener, actualizar y eliminar tareas dentro de una lista.
3. Cambiar el estado de una tarea.
4. Listar todas las tareas de una lista con filtros por estado o prioridad, y un campo extra con el porcentaje de completitud.

### b. Suman puntos (opcionales)

1. Login y autenticación: JWT para proteger endpoints.
2. Asignación de tareas: asignar un usuario responsable a cada tarea.
3. Notificación ficticia: simulación de envío de invitación a usuarios por email (no real).

## 2. Estructura del proyecto

a. Estructura limpia por capas (Domain, Application/UseCases, Infrastructure).
b. Tipado fuerte con Pydantic.
c. Manejo de errores con excepciones personalizadas.
d. Validaciones de negocio.
e. Testing unitario y de integración con pytest.
f. Linters (flake8, ruff) y formateo (black, isort).
g. Dockerfile (multistage si aplica) y docker-compose.
h. README completo + `DECISION_LOG.md` explicando decisiones técnicas.

## 3. Testing

a. Pruebas unitarias y de integración con pytest.
b. Cobertura mínima del 75% del proyecto.
c. Archivo `pytest.ini` para configurar pytest.

## 4. Linter y formateo

a. flake8 como linter.
b. black como formateador.
c. Archivo `.flake8` con configuraciones (por ejemplo, reglas ignoradas).

## 5. Docker

a. Dockerfile para construir la imagen de la aplicación.
b. `docker-compose.yml` (opcional) para facilitar el levantamiento.

## 6. README

Debe incluir:
- Descripción del proyecto.
- Instrucciones para configurar el entorno local.
- Instrucciones para ejecutar la aplicación en Docker.
- Instrucciones para correr las pruebas.

## Checklist de entregables

- [ ] Código por capas (domain / application / infrastructure)
- [ ] CRUD de listas
- [ ] CRUD de tareas
- [ ] Cambio de estado
- [ ] Listado con filtros + porcentaje de completitud
- [ ] Excepciones personalizadas + validaciones de negocio
- [ ] Tests unitarios + integración, cobertura ≥ 75%
- [ ] `pytest.ini`
- [ ] `.flake8` + black + isort configurados
- [ ] `Dockerfile` (multistage) + `docker-compose.yml`
- [ ] `README.md`
- [ ] `DECISION_LOG.md` (incluye sección de pendientes)
