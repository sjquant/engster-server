from .auth import blueprint as auth_bp
from .subtitle import blueprint as subtitle_bp
from .mypage import blueprint as mypage_bp
from .upload import blueprint as upload_bp


def init_app(app):
    app.static("/media", "./media")
    app.blueprint(auth_bp)
    app.blueprint(subtitle_bp)
    app.blueprint(mypage_bp)
    app.blueprint(upload_bp)
