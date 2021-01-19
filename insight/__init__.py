__version__ = "0.1.0"

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from flask_migrate import Migrate

from .app import app as dash_app


db = SQLAlchemy()


def create_app():
    "Create and configure the app."
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(os.environ["APP_SETTINGS"])

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    dash_app.init_app(app)

    migrate = Migrate(app, db)

    for name, method in dash_app.server.view_functions.items():
        app.logger.debug(f"view function: {name} ({method})")
        if not name.startswith(auth_blueprint.name):
            dash_app.server.view_functions[name] = login_required(method)

    return app
