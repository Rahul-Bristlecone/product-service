from unittest.mock import patch

import pytest
from flask import Flask

from src.product.main import create_app


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000, http://localhost:5000")
    monkeypatch.setenv("MYSQL_USER", "user")
    monkeypatch.setenv("MYSQL_PASSWORD", "pass")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "3306")
    monkeypatch.setenv("MYSQL_DATABASE", "product_db")
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")


def _create_app_without_db_side_effects():
    # The app factory currently calls db.create_all(), so we patch it to keep tests unit-level.
    with patch("src.product.main.db.create_all") as _create_all:
        return create_app()


def test_create_app_builds_flask_app_with_expected_core_config(env_vars):
    app = _create_app_without_db_side_effects()

    assert isinstance(app, Flask)
    assert app.config["API_TITLE"] == "Product service API"
    assert app.config["API_VERSION"] == "v1"
    assert app.config["OPENAPI_VERSION"] == "3.0.3"
    assert app.config["JWT_TOKEN_LOCATION"] == ["headers"]
    assert app.config["JWT_SECRET_KEY"] == "secret"


def test_create_app_sets_database_uri_from_environment(env_vars):
    app = _create_app_without_db_side_effects()

    assert (
        app.config["SQLALCHEMY_DATABASE_URI"]
        == "mysql+pymysql://user:pass@localhost:3306/product_db"
    )


def test_create_app_registers_health_route(env_vars):
    app = _create_app_without_db_side_effects()

    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_create_app_registers_swagger_ui_endpoint(env_vars):
    app = _create_app_without_db_side_effects()

    response = app.test_client().get("/swagger-ui")

    assert response.status_code in (200, 301, 302, 307, 308)


def test_create_app_requires_allowed_origins_env_var(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)

    with pytest.raises(AttributeError):
        create_app()
