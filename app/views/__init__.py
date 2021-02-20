from .auth import blueprint as auth_bp
from .user import blueprint as user_bp
from .subtitle import blueprint as subtitle_bp
from .translation import blueprint as translation_bp
from .content import blueprint as content_bp
from .genre import blueprint as genre_bp
from .file import blueprint as file_bp


def init_app(app):
    app.static("/media", "./media")
    app.blueprint(auth_bp)
    app.blueprint(user_bp)
    app.blueprint(subtitle_bp)
    app.blueprint(translation_bp)
    app.blueprint(content_bp)
    app.blueprint(genre_bp)
    app.blueprint(file_bp)
