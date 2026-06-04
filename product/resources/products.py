import json
from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from product.extentions.db import db
from product.extentions.redis_client import redis_client
from product.models.product_model import ProductModel
from product.schemas.product_schema import ProductSchema

# Create blueprint for Products
blp = Blueprint("products", __name__, description="Operations on products")


def validate_active_session(user_id):
    auth_header = request.headers.get("Authorization", "")
    token_parts = auth_header.split()
    if len(token_parts) != 2:
        abort(401, message="Missing or invalid authorization token")

    token = token_parts[1]
    cached_session = redis_client.get(f"session:{user_id}")
    if not cached_session:
        abort(401, message="Session expired or revoked")

    try:
        session_data = json.loads(cached_session)
        cached_token = session_data.get("token")
    except Exception:
        abort(401, message="Invalid session data")

    if cached_token != token:
        abort(401, message="Session expired or revoked")


def get_user_product_or_404(product_id, user_id):
    product = ProductModel.query.filter_by(product_id=product_id, user_id=user_id).first()
    if not product:
        abort(404, message="Product not found")
    return product

def create_product_from_payload(product_data):
    """
    Shared logic to create an order in the database.
    Validates JWT, checks Redis session, and persists the order.
    """
    user_id = int(get_jwt_identity())
    validate_active_session(user_id)

    # Inject user_id from JWT
    product = ProductModel(user_id=user_id, **product_data)

    try:
        db.session.add(product)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, message="Product code already exists")
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="Error inserting order into database")

    return product


# -------------------------------
# Endpoint: /create_product
# -------------------------------
@blp.route("/create_product")
class OrderCreate(MethodView):
    @jwt_required()
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data):
        return create_product_from_payload(product_data)

# more endpoints to be added
# -------------------------------
# Endpoint: /product/<product_id>
# -------------------------------
@blp.route("/product/<int:product_id>")
class OrderResource(MethodView):
    @jwt_required()
    @blp.response(200, ProductSchema)
    def get(self, product_id):
        user_id = int(get_jwt_identity())
        validate_active_session(user_id)
        product = get_user_product_or_404(product_id, user_id)
        return product

    @jwt_required()
    @blp.arguments(ProductSchema(partial=True))
    @blp.response(200, ProductSchema)
    def put(self, product_data, product_id):
        user_id = int(get_jwt_identity())
        validate_active_session(user_id)

        product = get_user_product_or_404(product_id, user_id)

        if "product_code" in product_data:
            abort(400, message="product_code cannot be updated")

        # Ensure product ownership cannot be reassigned via request payload.
        product_data.pop("user_id", None)
        product_data.pop("product_id", None)

        for key, value in product_data.items():
            setattr(product, key, value)

        try:
            db.session.add(product)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Product code or barcode already exists")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Error updating product in database")

        return product

    @jwt_required()
    def delete(self, product_id):
        user_id = int(get_jwt_identity())
        validate_active_session(user_id)

        product = get_user_product_or_404(product_id, user_id)

        try:
            db.session.delete(product)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Error deleting product from database")

        return {"message": "Product deleted successfully"}, 200


# -------------------------------
# Endpoint: /products
# -------------------------------
@blp.route("/products")
class OrderList(MethodView):
    @jwt_required()
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        user_id = int(get_jwt_identity())
        return ProductModel.query.filter_by(user_id=user_id).all()


# To upload product data using csv or excel sheet   
# @blp.route("/upload_product_data")
# class UploadEdiResource(MethodView):
#     @jwt_required()
#     @blp.response(201, ProductSchema)
#     def post(self):
#         if "file" not in request.files:
#             abort(400, message="No file uploaded")

#         edi_file = request.files["file"]
#         file_path = os.path.join("/tmp", edi_file.filename)
#         edi_file.save(file_path)

#         # Transform csv data → JSON
#         order_data = transform_csv_to_json(file_path)

#         # Reuse the same order creation logic
#         return create_order_from_payload(order_data)