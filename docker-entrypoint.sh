#!/bin/sh
set -e

# Alembic gestiona el esquema (A6): la app nunca llama a create_all().
alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
