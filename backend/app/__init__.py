from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_jwt import initialize
from sanic_cors import CORS
from simple_bcrypt import Bcrypt

db = Gino()
bcrypt = Bcrypt()


def init_auth(app):
    from app.core.auth import authenticate, CustomResponse
    initialize(app,
               authenticate=authenticate,
               url_prefix='auth',
               path_to_authenticate='/obtain_token',
               path_to_retrieve_user='/retrieve_user',
               path_to_verify='/verify_token',
               path_to_refresh='/refresh_token',
               claim_iss='engster.co.kr',
               refresh_token_enabled=False,  # Temporarily
               responses_class=CustomResponse
               )


def create_app(config):
    """
    Create Sanic Application
    """
    app = Sanic()
    app.config.from_object(config)
    db.init_app(app)
    CORS(app, origins=app.config.get('ORIGINS', '*'))
    bcrypt.init_app(app)
    init_auth(app)

    from app import routers
    routers.init_app(app)

    return app
