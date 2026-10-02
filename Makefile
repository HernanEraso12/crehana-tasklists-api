.PHONY: install test lint format up

install:
	uv sync

test:
	uv run pytest

lint:
	uv run flake8

format:
	uv run black .
	uv run isort .

up:
	docker compose up --build
