from src.product import create_app


def test_package_exports_create_app():
    assert callable(create_app)
