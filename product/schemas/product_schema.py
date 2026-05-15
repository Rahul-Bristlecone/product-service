from marshmallow import Schema, fields, validate


class ProductSchema(Schema):
    product_id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    product_code = fields.Str(
        required=True,
        validate=validate.Regexp(r"^[A-Za-z0-9]+$", error="product_code must be alphanumeric"),
    )
    barcode = fields.Str(required=True)  # changed from Int to Str
    price = fields.Float(required=True)
    tax_rate = fields.Float(allow_none=True)
    expiry_date = fields.Date(allow_none=True)
    pack_size = fields.Str(allow_none=True)

    terminated = fields.Int(load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    hazardous = fields.Int(load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    allow_pick_by_product = fields.Int(load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))

