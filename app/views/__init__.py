from .auth import blueprint as auth_bp
from .search import blueprint as search_bp
from .like import blueprint as like_bp
from .admin import blueprint as admin_bp
from .translation import blueprint as translation_bp
from .mypage import blueprint as mypage_bp


def init_app(app):
    app.blueprint(auth_bp)
    app.blueprint(search_bp)
    app.blueprint(like_bp)
    app.blueprint(admin_bp)
    app.blueprint(translation_bp)
    app.blueprint(mypage_bp)
