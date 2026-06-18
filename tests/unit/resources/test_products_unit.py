import json
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from product.resources.products import (
    create_product_from_payload,
    get_user_product_or_404,
    validate_active_session,
)


@pytest.fixture
def request_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


class TestValidateActiveSession:
    def test_accepts_valid_session(self, request_app):
        with request_app.test_request_context(
            "/products", headers={"Authorization": "Bearer valid_token"}
        ):
            with patch("product.resources.products.redis_client") as mock_redis:
                mock_redis.get.return_value = json.dumps({"token": "valid_token"}).encode()

                validate_active_session(100)

                mock_redis.get.assert_called_once_with("session:100")

    def test_rejects_missing_or_invalid_authorization_header(self, request_app):
        with request_app.test_request_context("/products", headers={}):
            with patch(
                "product.resources.products.abort", side_effect=RuntimeError("abort")
            ) as mock_abort:
                with pytest.raises(RuntimeError, match="abort"):
                    validate_active_session(100)

                mock_abort.assert_called_once_with(
                    401, message="Missing or invalid authorization token"
                )

    def test_rejects_missing_cached_session(self, request_app):
        with request_app.test_request_context(
            "/products", headers={"Authorization": "Bearer valid_token"}
        ):
            with patch("product.resources.products.redis_client") as mock_redis, patch(
                "product.resources.products.abort", side_effect=RuntimeError("abort")
            ) as mock_abort:
                mock_redis.get.return_value = None

                with pytest.raises(RuntimeError, match="abort"):
                    validate_active_session(100)

                mock_abort.assert_called_once_with(401, message="Session expired or revoked")

    def test_rejects_invalid_cached_session_json(self, request_app):
        with request_app.test_request_context(
            "/products", headers={"Authorization": "Bearer valid_token"}
        ):
            with patch("product.resources.products.redis_client") as mock_redis, patch(
                "product.resources.products.abort", side_effect=RuntimeError("abort")
            ) as mock_abort:
                mock_redis.get.return_value = "not-json"

                with pytest.raises(RuntimeError, match="abort"):
                    validate_active_session(100)

                mock_abort.assert_called_once_with(401, message="Invalid session data")

    def test_rejects_token_mismatch(self, request_app):
        with request_app.test_request_context(
            "/products", headers={"Authorization": "Bearer live_token"}
        ):
            with patch("product.resources.products.redis_client") as mock_redis, patch(
                "product.resources.products.abort", side_effect=RuntimeError("abort")
            ) as mock_abort:
                mock_redis.get.return_value = json.dumps({"token": "cached_token"}).encode()

                with pytest.raises(RuntimeError, match="abort"):
                    validate_active_session(100)

                mock_abort.assert_called_once_with(401, message="Session expired or revoked")


class TestGetUserProductOr404:
    def test_returns_product_for_owner(self, sample_product):
        with patch("product.resources.products.ProductModel") as mock_model:
            mock_model.query.filter_by.return_value.first.return_value = sample_product

            result = get_user_product_or_404(1, 100)

            assert result is sample_product
            mock_model.query.filter_by.assert_called_once_with(product_id=1, user_id=100)

    def test_aborts_when_product_not_found(self):
        with patch("product.resources.products.ProductModel") as mock_model, patch(
            "product.resources.products.abort", side_effect=RuntimeError("abort")
        ) as mock_abort:
            mock_model.query.filter_by.return_value.first.return_value = None

            with pytest.raises(RuntimeError, match="abort"):
                get_user_product_or_404(999, 100)

            mock_abort.assert_called_once_with(404, message="Product not found")


class TestCreateProductFromPayload:
    def test_persists_product_on_success(self, product_payload):
        with patch("product.resources.products.get_jwt_identity", return_value="100"), patch(
            "product.resources.products.validate_active_session"
        ) as mock_validate, patch(
            "product.resources.products.ProductModel"
        ) as mock_product_model, patch(
            "product.resources.products.db"
        ) as mock_db:
            created_product = MagicMock(name="product")
            mock_product_model.return_value = created_product

            result = create_product_from_payload(product_payload)

            assert result is created_product
            mock_validate.assert_called_once_with(100)
            mock_product_model.assert_called_once_with(user_id=100, **product_payload)
            mock_db.session.add.assert_called_once_with(created_product)
            mock_db.session.commit.assert_called_once()

    def test_rolls_back_and_aborts_on_integrity_error(self, product_payload):
        with patch("product.resources.products.get_jwt_identity", return_value="100"), patch(
            "product.resources.products.validate_active_session"
        ), patch("product.resources.products.ProductModel"), patch(
            "product.resources.products.db"
        ) as mock_db, patch(
            "product.resources.products.abort", side_effect=RuntimeError("abort")
        ) as mock_abort:
            mock_db.session.commit.side_effect = IntegrityError(
                "insert", {"product_code": "PROD001"}, Exception("duplicate")
            )

            with pytest.raises(RuntimeError, match="abort"):
                create_product_from_payload(product_payload)

            mock_db.session.rollback.assert_called_once()
            mock_abort.assert_called_once_with(400, message="Product code already exists")

    def test_rolls_back_and_aborts_on_sqlalchemy_error(self, product_payload):
        with patch("product.resources.products.get_jwt_identity", return_value="100"), patch(
            "product.resources.products.validate_active_session"
        ), patch("product.resources.products.ProductModel"), patch(
            "product.resources.products.db"
        ) as mock_db, patch(
            "product.resources.products.abort", side_effect=RuntimeError("abort")
        ) as mock_abort:
            mock_db.session.commit.side_effect = SQLAlchemyError("db-failure")

            with pytest.raises(RuntimeError, match="abort"):
                create_product_from_payload(product_payload)

            mock_db.session.rollback.assert_called_once()
            mock_abort.assert_called_once_with(
                500, message="Error inserting order into database"
            )
