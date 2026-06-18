from datetime import date

import pytest

from product.models.product_model import ProductModel


@pytest.fixture
def product_payload():
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
    product = ProductModel(
        user_id=100,
        product_code="PROD001",
        barcode="123456789",
        price=99.99,
        tax_rate=0.18,
        expiry_date=date(2025, 12, 31),
        pack_size="1kg",
        terminated=False,
        hazardous=False,
        allow_pick_by_product=True,
    )
    product.product_id = 1
    return product
