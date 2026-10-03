# syntax=docker/dockerfile:1

# ---- builder: instala dependencias de producción con uv (A5) ----
FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

# Capa de dependencias por separado del código: cambios en src/ no
# invalidan esta capa, que es la más pesada (descarga de paquetes).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN uv sync --frozen --no-dev


# ---- final: imagen slim, sin uv, usuario no root (D4) ----
FROM python:3.12-slim AS final

RUN useradd --create-home --uid 1000 --shell /bin/sh appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src ./src
COPY alembic.ini ./
COPY alembic ./alembic
COPY docker-entrypoint.sh ./

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN chmod +x docker-entrypoint.sh && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
