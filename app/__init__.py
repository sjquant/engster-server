from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_jwt import initialize
from sanic_cors import CORS


db = Gino()


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


def create_app(env: str = 'local'):
    """
    Create Sanic Application
    """
    from app.utils.config import get_config
    config = get_config(env)

    app = Sanic()
    app.config.from_object(config)
    db.init_app(app)
    CORS(app, origins=app.config.get('ORIGINS', '*'))
    init_auth(app)

    from app import views
    views.init_app(app)

    return app
