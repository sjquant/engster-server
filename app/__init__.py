import os
import importlib

from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_jwt_extended import JWTManager
from sanic_cors import CORS


db = Gino()


def get_config():
    env = os.getenv("ENV", "development")
    config = importlib.import_module(f"app.config.{env}")
    return config


def init_config(app):
    app.config.from_object(get_config())


def create_app():
    """
    Create Sanic Application
    """
    app = Sanic()
    init_config(app)

    CORS(app, automatic_options=True)
    db.init_app(app)

    JWTManager(app)
    from app import views

    views.init_app(app)
    return app
