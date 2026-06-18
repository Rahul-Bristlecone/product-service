import pytest
from marshmallow import ValidationError

from product.schemas.product_schema import ProductSchema


def test_product_schema_loads_valid_payload(product_payload):
    schema = ProductSchema()

    loaded = schema.load(product_payload)

    assert loaded["product_code"] == "PROD001"
    assert loaded["barcode"] == "123456789"
    assert loaded["price"] == 99.99
    assert loaded["terminated"] == 0
    assert loaded["hazardous"] == 0
    assert loaded["allow_pick_by_product"] == 1


def test_product_schema_rejects_invalid_product_code_characters(product_payload):
    schema = ProductSchema()
    product_payload["product_code"] = "PROD-001"

    with pytest.raises(ValidationError) as exc:
        schema.load(product_payload)

    assert "product_code" in exc.value.messages


def test_product_schema_rejects_invalid_boolean_flags(product_payload):
    schema = ProductSchema()
    product_payload["terminated"] = 2

    with pytest.raises(ValidationError) as exc:
        schema.load(product_payload)

    assert "terminated" in exc.value.messages


def test_product_schema_applies_default_values_for_flags(product_payload):
    schema = ProductSchema()
    product_payload.pop("terminated")
    product_payload.pop("hazardous")
    product_payload.pop("allow_pick_by_product")

    loaded = schema.load(product_payload)

    assert loaded["terminated"] == 0
    assert loaded["hazardous"] == 0
    assert loaded["allow_pick_by_product"] == 0


def test_product_schema_dump_hides_dump_only_inputs(sample_product):
    schema = ProductSchema()

    dumped = schema.dump(sample_product)

    assert dumped["product_id"] == 1
    assert dumped["user_id"] == 100
    assert dumped["product_code"] == "PROD001"
