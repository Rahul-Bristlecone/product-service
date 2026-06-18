import importlib


def test_redis_client_uses_env_values(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "cache.internal")
    monkeypatch.setenv("REDIS_PORT", "6380")
    monkeypatch.setenv("REDIS_PASSWORD", "mypassword")

    module = importlib.import_module("src.product.extentions.redis_client")
    module = importlib.reload(module)

    kwargs = module.redis_client.connection_pool.connection_kwargs
    assert kwargs["host"] == "cache.internal"
    assert kwargs["port"] == 6380
    assert kwargs["password"] == "mypassword"


def test_redis_client_sets_empty_password_to_none(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "cache.internal")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_PASSWORD", "")

    module = importlib.import_module("src.product.extentions.redis_client")
    module = importlib.reload(module)

    kwargs = module.redis_client.connection_pool.connection_kwargs
    assert kwargs["password"] is None
