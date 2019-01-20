from .auth import auth_bp


def init_app(app):
    app.blueprint(auth_bp)
