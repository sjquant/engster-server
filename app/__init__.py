import aiohttp
from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_cors import CORS
from sanic_jwt_extended.jwt_manager import JWT

from app import config

db = Gino()


def init_jwt(app):
    from app.utils import encode_jwt

    JWT._encode_jwt = classmethod(encode_jwt)
    with JWT.initialize(app) as manager:
        manager.config.public_claim_namespace = config.JWT["namespace"]
        manager.config.private_claim_prefix = config.JWT["private_claim_prefix"]
        manager.config.secret_key = config.JWT["secret_key"]
        manager.config.token_location = config.JWT["token_location"]
        manager.config.access_token_expires = config.JWT["access_expires"]
        manager.config.cookie_secure = config.JWT["cookie_secure"]
        manager.config.jwt_csrf_header = config.JWT["jwt_csrf_header"]
        manager.config.refresh_jwt_csrf_header = config.JWT["refresh_jwt_csrf_header"]
        manager.config.csrf_protect = config.JWT["csrf_protect"]
        manager.config.cookie_domain = config.JWT["cookie_domain"]


def init_oauth(app):
    @app.listener("after_server_start")
    async def init_aiohttp_session(sanic_app, _loop) -> None:
        sanic_app.async_session = aiohttp.ClientSession()

    @app.listener("before_server_stop")
    async def close_aiohttp_session(sanic_app, _loop) -> None:
        await sanic_app.async_session.close()


def create_app():
    """
    Create Sanic Application
    """
    app = Sanic()
    app.config.from_object(config)
    init_oauth(app)
    init_jwt(app)

    CORS(app)
    db.init_app(app)
    from app import views

    views.init_app(app)
    return app
