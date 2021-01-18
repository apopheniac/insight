from flask import Flask

from .app import app as dash_app


def create_app():
    "Create and configure the app."
    app = Flask(__name__, instance_relative_config=True)

    dash_app.init_app(app)

    return app
