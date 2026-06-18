from src.product.models.product_model import ProductModel


def test_product_model_table_name_is_products():
    assert ProductModel.__tablename__ == "products"


def test_product_model_has_expected_unique_constraints():
    constraint_names = {
        constraint.name
        for constraint in ProductModel.__table_args__
        if hasattr(constraint, "name")
    }

    assert "uq_products_user_product_code" in constraint_names
    assert "uq_products_user_barcode" in constraint_names


def test_product_model_default_boolean_values_are_false():
    product = ProductModel(
        user_id=101,
        product_code="CODE1",
        barcode="B001",
        price=10.0,
    )

    assert product.terminated is None or product.terminated is False
    assert product.hazardous is None or product.hazardous is False
    assert product.allow_pick_by_product is None or product.allow_pick_by_product is False
