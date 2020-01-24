import os
import importlib

import aiohttp
from sanic import Sanic
from gino.ext.sanic import Gino
from sanic_jwt_extended import JWT
from sanic_cors import CORS

from app import config

db = Gino()


def init_jwt(app):
    with JWT.initialize(app) as manager:
        manager.config.secret_key = config.JWT["secret_key"]
        manager.config.access_token_expires = config.JWT["access_expires"]


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

    CORS(app, automatic_options=True)
    db.init_app(app)
    from app import views

    views.init_app(app)
    return app
