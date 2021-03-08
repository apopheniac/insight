# models.py
from uuid import uuid4
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON

from . import db


class User(UserMixin, db.Model):
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Dataset(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    spreadsheet_id = db.Column(db.String, nullable=False)
    spreadsheet_range = db.Column(db.String, nullable=False)
    spreadsheet_hash = db.Column(db.String(64), index=True, nullable=False)
    data = db.Column(JSON, nullable=False)
