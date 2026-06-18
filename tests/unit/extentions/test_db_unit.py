from flask_sqlalchemy import SQLAlchemy

from product.extentions.db import db


def test_db_extension_is_sqlalchemy_instance():
    assert isinstance(db, SQLAlchemy)
