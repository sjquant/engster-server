from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_jwt import initialize

from app.core.auth import PasswordHasher

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

    from app.utils.auth import authenticate
    initialize(app,
               authenticate=authenticate,
               path_to_authenticate='/auth/obtain_token',
               path_to_verify='/auth/verify_token',
               path_to_refresh='/auth/refresh_token'
               )

    return app
