from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_jwt import initialize

from simple_bcrypt import Bcrypt

db = Gino()
bcrypt = Bcrypt()


def init_auth(app):
    from app.utils.auth import authenticate
    initialize(app,
               authenticate=authenticate,
               url_prefix='auth',
               path_to_authenticate='/obtain_token',
               path_to_retrieve_user='/retrieve_user',
               path_to_verify='/verify_token',
               path_to_refresh='/refresh_token',
               claim_iss='engster.co.kr'
               )


def create_app(config_file):
    """
    Create Sanic Application
    """
    app = Sanic()
    app.config.from_object(config_file)

    db.init_app(app)
    bcrypt.init_app(app)
    init_auth(app)

    return app
