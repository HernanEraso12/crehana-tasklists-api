"""Test trivial de Fase 0: valida que pytest, la cobertura y el paquete `app`
quedaron correctamente configurados antes de empezar con TDD de dominio."""


def test_pytest_runs() -> None:
    assert 1 + 1 == 2


def test_app_package_is_importable() -> None:
    from app.main import app

    assert app.title == "Crehana Task Lists API"


def test_settings_have_a_database_url() -> None:
    from app.infrastructure.config import Settings

    settings = Settings(_env_file=None)

    assert settings.database_url
