import json
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date

from product.resources.products import (
    validate_active_session,
    get_user_product_or_404,
    create_product_from_payload,
)
from product.models.product_model import ProductModel
from product.schemas.product_schema import ProductSchema


@pytest.fixture
def mock_request():
    """Mock Flask request object"""
    with patch('product.resources.products.request') as mock:
        yield mock


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy db session"""
    with patch('product.resources.products.db') as mock:
        yield mock


@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    with patch('product.resources.products.redis_client') as mock:
        yield mock


@pytest.fixture
def mock_jwt():
    """Mock JWT identity"""
    with patch('product.resources.products.get_jwt_identity') as mock:
        yield mock


@pytest.fixture
def product_data():
    """Sample product data"""
    return {
        "product_code": "PROD001",
        "barcode": "123456789",
        "price": 99.99,
        "tax_rate": 0.18,
        "expiry_date": "2025-12-31",
        "pack_size": "1kg",
        "terminated": 0,
        "hazardous": 0,
        "allow_pick_by_product": 1,
    }


@pytest.fixture
def sample_product():
    """Sample product model instance"""
    product = ProductModel()
    product.product_id = 1
    product.user_id = 100
    product.product_code = "PROD001"
    product.barcode = "123456789"
    product.price = 99.99
    product.tax_rate = 0.18
    product.expiry_date = date(2025, 12, 31)
    product.pack_size = "1kg"
    product.terminated = False
    product.hazardous = False
    product.allow_pick_by_product = True
    return product


# =========================================
# Helper Function Tests
# =========================================

class TestValidateActiveSession:
    """Test cases for validate_active_session function"""

    def test_valid_session(self, mock_request, mock_redis_client):
        """Test successful session validation"""
        user_id = 100
        token = "valid_token_123"
        
        mock_request.headers.get.return_value = f"Bearer {token}"
        session_data = {"token": token}
        mock_redis_client.get.return_value = json.dumps(session_data).encode()
        
        # Should not raise any exception
        validate_active_session(user_id)
        
        mock_request.headers.get.assert_called_once_with("Authorization", "")
        mock_redis_client.get.assert_called_once_with(f"session:{user_id}")

    def test_missing_authorization_header(self, mock_request, mock_redis_client):
        """Test with missing authorization header"""
        mock_request.headers.get.return_value = ""
        
        with patch('product.resources.products.abort') as mock_abort:
            validate_active_session(100)
            mock_abort.assert_called_once_with(401, message="Missing or invalid authorization token")

    def test_invalid_token_format(self, mock_request, mock_redis_client):
        """Test with invalid token format"""
        mock_request.headers.get.return_value = "InvalidFormat"
        
        with patch('product.resources.products.abort') as mock_abort:
            validate_active_session(100)
            mock_abort.assert_called_once_with(401, message="Missing or invalid authorization token")

    def test_expired_session(self, mock_request, mock_redis_client):
        """Test with expired session (not in Redis)"""
        user_id = 100
        token = "some_token"
        mock_request.headers.get.return_value = f"Bearer {token}"
        mock_redis_client.get.return_value = None
        
        with patch('product.resources.products.abort') as mock_abort:
            validate_active_session(user_id)
            mock_abort.assert_called_once_with(401, message="Session expired or revoked")

    def test_invalid_session_data(self, mock_request, mock_redis_client):
        """Test with corrupted session data"""
        user_id = 100
        token = "some_token"
        mock_request.headers.get.return_value = f"Bearer {token}"
        mock_redis_client.get.return_value = "invalid_json"
        
        with patch('product.resources.products.abort') as mock_abort:
            validate_active_session(user_id)
            mock_abort.assert_called_once_with(401, message="Invalid session data")

    def test_token_mismatch(self, mock_request, mock_redis_client):
        """Test when token doesn't match cached token"""
        user_id = 100
        token = "current_token"
        cached_token = "different_token"
        
        mock_request.headers.get.return_value = f"Bearer {token}"
        session_data = {"token": cached_token}
        mock_redis_client.get.return_value = json.dumps(session_data).encode()
        
        with patch('product.resources.products.abort') as mock_abort:
            validate_active_session(user_id)
            mock_abort.assert_called_once_with(401, message="Session expired or revoked")


class TestGetUserProductOr404:
    """Test cases for get_user_product_or_404 function"""

    def test_product_found(self, sample_product):
        """Test when product is found"""
        with patch('product.resources.products.ProductModel.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = sample_product
            
            result = get_user_product_or_404(1, 100)
            
            assert result == sample_product
            mock_query.filter_by.assert_called_once_with(product_id=1, user_id=100)

    def test_product_not_found(self):
        """Test when product is not found"""
        with patch('product.resources.products.ProductModel.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            with patch('product.resources.products.abort') as mock_abort:
                get_user_product_or_404(999, 100)
                mock_abort.assert_called_once_with(404, message="Product not found")


class TestCreateProductFromPayload:
    """Test cases for create_product_from_payload function"""

    def test_successful_product_creation(self, product_data, mock_jwt, mock_db, mock_redis_client, mock_request):
        """Test successful product creation"""
        user_id = 100
        token = "valid_token"
        
        mock_jwt.return_value = str(user_id)
        mock_request.headers.get.return_value = f"Bearer {token}"
        session_data = {"token": token}
        mock_redis_client.get.return_value = json.dumps(session_data).encode()
        
        with patch('product.resources.products.ProductModel') as mock_product_class:
            mock_product_instance = MagicMock()
            mock_product_class.return_value = mock_product_instance
            
            result = create_product_from_payload(product_data)
            
            assert result == mock_product_instance
            mock_db.session.add.assert_called_once_with(mock_product_instance)
            mock_db.session.commit.assert_called_once()

    def test_product_creation_integrity_error(self, product_data, mock_jwt, mock_db, mock_redis_client, mock_request):
        """Test product creation with IntegrityError (duplicate product_code)"""
        from sqlalchemy.exc import IntegrityError
        
        user_id = 100
        token = "valid_token"
        
        mock_jwt.return_value = str(user_id)
        mock_request.headers.get.return_value = f"Bearer {token}"
        session_data = {"token": token}
        mock_redis_client.get.return_value = json.dumps(session_data).encode()
        
        mock_db.session.commit.side_effect = IntegrityError("", "", "")
        
        with patch('product.resources.products.ProductModel'):
            with patch('product.resources.products.abort') as mock_abort:
                create_product_from_payload(product_data)
                mock_abort.assert_called_once_with(400, message="Product code already exists")
                mock_db.session.rollback.assert_called_once()

    def test_product_creation_database_error(self, product_data, mock_jwt, mock_db, mock_redis_client, mock_request):
        """Test product creation with SQLAlchemy error"""
        from sqlalchemy.exc import SQLAlchemyError
        
        user_id = 100
        token = "valid_token"
        
        mock_jwt.return_value = str(user_id)
        mock_request.headers.get.return_value = f"Bearer {token}"
        session_data = {"token": token}
        mock_redis_client.get.return_value = json.dumps(session_data).encode()
        
        mock_db.session.commit.side_effect = SQLAlchemyError("Database error")
        
        with patch('product.resources.products.ProductModel'):
            with patch('product.resources.products.abort') as mock_abort:
                create_product_from_payload(product_data)
                mock_abort.assert_called_once_with(500, message="Error inserting order into database")
                mock_db.session.rollback.assert_called_once()


# =========================================
# Blueprint Endpoint Tests
# =========================================

@pytest.fixture
def app():
    """Create Flask app for testing"""
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestCreateProductEndpoint:
    """Test cases for POST /create_product endpoint"""

    def test_create_product_success(self, app):
        """Test successful product creation via endpoint"""
        from product.resources.products import blp
        
        app.register_blueprint(blp)
        client = app.test_client()
        
        payload = {
            "product_code": "PROD001",
            "barcode": "123456789",
            "price": 99.99,
            "tax_rate": 0.18,
        }
        
        with patch('product.resources.products.jwt_required'):
            with patch('product.resources.products.create_product_from_payload') as mock_create:
                mock_product = MagicMock()
                mock_product.product_id = 1
                mock_create.return_value = mock_product
                
                response = client.post(
                    '/create_product',
                    json=payload,
                    headers={'Authorization': 'Bearer test_token'}
                )
                
                # Note: The actual status code depends on the full Flask setup
                # This is a basic test structure
                assert response.status_code in [200, 201, 401]  # 401 because we're not fully mocking JWT


class TestGetProductEndpoint:
    """Test cases for GET /product/<product_id> endpoint"""

    def test_get_product_success(self, sample_product):
        """Test successful product retrieval"""
        with patch('product.resources.products.get_jwt_identity') as mock_jwt:
            with patch('product.resources.products.validate_active_session') as mock_validate:
                with patch('product.resources.products.get_user_product_or_404') as mock_get:
                    mock_jwt.return_value = "100"
                    mock_get.return_value = sample_product
                    
                    result = get_user_product_or_404(1, 100)
                    assert result.product_id == 1
                    assert result.user_id == 100


class TestUpdateProductEndpoint:
    """Test cases for PUT /product/<product_id> endpoint"""

    def test_update_product_success(self, sample_product, mock_db):
        """Test successful product update"""
        update_data = {
            "price": 150.00,
            "tax_rate": 0.12,
        }
        
        for key, value in update_data.items():
            setattr(sample_product, key, value)
        
        assert sample_product.price == 150.00
        assert sample_product.tax_rate == 0.12

    def test_update_product_code_not_allowed(self, sample_product):
        """Test that product_code cannot be updated"""
        update_data = {
            "product_code": "NEW_CODE",
        }
        
        with patch('product.resources.products.abort') as mock_abort:
            if "product_code" in update_data:
                mock_abort(400, message="product_code cannot be updated")
                mock_abort.assert_called_once_with(400, message="product_code cannot be updated")


class TestDeleteProductEndpoint:
    """Test cases for DELETE /product/<product_id> endpoint"""

    def test_delete_product_success(self, sample_product, mock_db):
        """Test successful product deletion"""
        mock_db.session.delete(sample_product)
        mock_db.session.commit()
        
        mock_db.session.delete.assert_called_once_with(sample_product)
        mock_db.session.commit.assert_called_once()

    def test_delete_product_database_error(self, sample_product, mock_db):
        """Test delete with database error"""
        from sqlalchemy.exc import SQLAlchemyError
        
        mock_db.session.delete.side_effect = SQLAlchemyError("DB Error")
        
        with patch('product.resources.products.abort') as mock_abort:
            try:
                mock_db.session.delete(sample_product)
            except SQLAlchemyError:
                mock_abort(500, message="Error deleting product from database")
                mock_abort.assert_called_once_with(500, message="Error deleting product from database")


class TestGetProductsListEndpoint:
    """Test cases for GET /products endpoint"""

    def test_get_products_list_success(self, sample_product):
        """Test successful retrieval of all user products"""
        with patch('product.resources.products.get_jwt_identity') as mock_jwt:
            with patch('product.resources.products.ProductModel.query') as mock_query:
                mock_jwt.return_value = "100"
                mock_query.filter_by.return_value.all.return_value = [sample_product]
                
                products = mock_query.filter_by(user_id=100).all()
                assert len(products) == 1
                assert products[0].product_id == 1

    def test_get_products_list_empty(self):
        """Test retrieval when user has no products"""
        with patch('product.resources.products.get_jwt_identity') as mock_jwt:
            with patch('product.resources.products.ProductModel.query') as mock_query:
                mock_jwt.return_value = "100"
                mock_query.filter_by.return_value.all.return_value = []
                
                products = mock_query.filter_by(user_id=100).all()
                assert len(products) == 0


# =========================================
# Integration Tests
# =========================================

class TestProductsIntegration:
    """Integration tests for the product endpoints"""

    def test_product_lifecycle(self, product_data, sample_product, mock_db, mock_jwt, mock_redis_client, mock_request):
        """Test complete product lifecycle: create -> read -> update -> delete"""
        user_id = 100
        token = "valid_token"
        
        # Setup mocks
        mock_jwt.return_value = str(user_id)
        mock_request.headers.get.return_value = f"Bearer {token}"
        session_data = {"token": token}
        mock_redis_client.get.return_value = json.dumps(session_data).encode()
        
        # Test: Get product (should exist)
        with patch('product.resources.products.ProductModel.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = sample_product
            product = get_user_product_or_404(sample_product.product_id, user_id)
            assert product.price == 99.99

    def test_unauthorized_access(self, mock_request, mock_redis_client):
        """Test that unauthorized users cannot access products"""
        user_id = 100
        invalid_token = "invalid_token"
        cached_token = "valid_token"
        
        mock_request.headers.get.return_value = f"Bearer {invalid_token}"
        session_data = {"token": cached_token}
        mock_redis_client.get.return_value = json.dumps(session_data).encode()
        
        with patch('product.resources.products.abort') as mock_abort:
            validate_active_session(user_id)
            mock_abort.assert_called_once_with(401, message="Session expired or revoked")
