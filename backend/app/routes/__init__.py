from .index import index_bp
from .auth import auth_bp
from .line import line_bp


def init_app(app):
    app.blueprint(index_bp)
    app.blueprint(auth_bp)
    app.blueprint(line_bp)
