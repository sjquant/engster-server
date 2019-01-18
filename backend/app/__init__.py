from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_jwt import initialize

from app.core import PasswordHasher
db = Gino()
hasher = PasswordHasher()


def create_app(config_file):
    """
    Create Sanic Application
    """
    app = Sanic()
    app.config.from_object(config_file)

    db.init_app(app)
    hasher.init_app(app)

    from app.utils import authenticate
    initialize(app, authenticate=authenticate)

    return app
