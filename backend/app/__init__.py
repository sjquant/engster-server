from sanic import Sanic
from gino.ext.sanic import Gino

db = Gino()


def create_app(config_file):
    """
    Create Sanic Application
    """
    app = Sanic()
    app.config.from_object(config_file)

    db.init_app(app)
    return app
