from .index import index_bp
from .auth import auth_bp
from .lines import lines_bp
from .admin import admin_bp


def init_app(app):
    app.blueprint(index_bp)
    app.blueprint(auth_bp)
    app.blueprint(lines_bp)
    app.blueprint(admin_bp)
