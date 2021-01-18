import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .app import app as dash_app


db = SQLAlchemy()
def create_app():
    "Create and configure the app."
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(os.environ["APP_SETTINGS"])

    db.init_app(app)
    from .models import User
    dash_app.init_app(app)

    migrate = Migrate(app, db)
    return app
