from src.product.extentions.db import db
# docker exec -it user-service bash
# python -m alembic revision --autogenerate -m "Added new column"
# python -m alembic upgrade head

class ProductModel(db.Model):
    __tablename__ = "products"

    __table_args__ = (
        db.UniqueConstraint("user_id", "product_code", name="uq_products_user_product_code"),
        db.UniqueConstraint("user_id", "barcode", name="uq_products_user_barcode")
    )

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    product_code = db.Column(db.String(64), nullable=False)
    barcode = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float)
    expiry_date = db.Column(db.Date)
    pack_size = db.Column(db.String(64))

    terminated = db.Column(db.Boolean, nullable=False, default=False)
    hazardous = db.Column(db.Boolean, nullable=False, default=False)
    allow_pick_by_product = db.Column(db.Boolean, nullable=False, default=False)
    
    