from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_jwt_extended import JWTManager
from sanic_cors import CORS


db = Gino()


def init_auth(app):
    JWTManager(app)


def create_app(env: str = 'local'):
    """
    Create Sanic Application
    """
    from app.utils.config import get_config
    config = get_config(env)

    app = Sanic()
    app.config.from_object(config)
    db.init_app(app)
    CORS(app, origins=app.config.get('ORIGINS', '*'), automatic_options=True)
    init_auth(app)

    from app import views
    views.init_app(app)

    return app
