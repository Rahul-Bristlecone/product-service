from unittest.mock import patch

from flask import Flask

from product.resources import health as health_module


def _build_app():
    app = Flask(__name__)
    app.register_blueprint(health_module.health_bp)
    return app


def test_startup_returns_down_until_startup_complete():
    health_module.startup_complete = False
    app = _build_app()

    response = app.test_client().get("/startup")

    assert response.status_code == 503
    assert response.get_json() == {"status": "DOWN"}


def test_startup_returns_up_when_startup_complete():
    health_module.startup_complete = True
    app = _build_app()

    response = app.test_client().get("/startup")

    assert response.status_code == 200
    assert response.get_json() == {"status": "UP"}


def test_readiness_returns_up_when_db_and_redis_are_healthy():
    app = _build_app()

    with patch.object(health_module, "db") as mock_db, patch.object(
        health_module, "redis_client"
    ) as mock_redis:
        mock_db.session.execute.return_value = 1
        mock_redis.ping.return_value = True

        response = app.test_client().get("/readiness")

        assert response.status_code == 200
        assert response.get_json() == {"status": "UP"}
        mock_db.session.execute.assert_called_once_with("SELECT 1")
        mock_redis.ping.assert_called_once()


def test_readiness_returns_down_when_dependency_check_fails():
    app = _build_app()

    with patch.object(health_module, "db") as mock_db, patch.object(
        health_module, "redis_client"
    ):
        mock_db.session.execute.side_effect = RuntimeError("db unavailable")

        response = app.test_client().get("/readiness")

        assert response.status_code == 503
        payload = response.get_json()
        assert payload["status"] == "DOWN"
        assert "db unavailable" in payload["error"]


def test_liveness_always_returns_up():
    app = _build_app()

    response = app.test_client().get("/liveness")

    assert response.status_code == 200
    assert response.get_json() == {"status": "UP"}
