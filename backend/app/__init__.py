from sanic import Sanic
from gino.ext.sanic import Gino
from simple_bcrypt import Bcrypt

db = Gino()
bcrypt = Bcrypt()


def create_app(config_file):
    """
    Create Sanic Application
    """
    app = Sanic()
    app.config.from_object(config_file)

    db.init_app(app)
    bcrypt.init_app(app)

    return app
