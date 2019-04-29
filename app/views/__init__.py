from sanic.response import json

from .base import blueprint as base_bp
from .auth import blueprint as auth_bp
from .search import blueprint as search_bp
from .like import blueprint as like_bp
from .admin import blueprint as admin_bp


async def hello_engster(request):
    return json({"Hello": "Engster"})


def init_app(app):

    app.add_route(hello_engster, '/')

    app.blueprint(base_bp)
    app.blueprint(auth_bp)
    app.blueprint(search_bp)
    app.blueprint(like_bp)
    app.blueprint(admin_bp)
