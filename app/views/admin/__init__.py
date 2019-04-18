from sanic.blueprints import Blueprint

from .subtitle import blueprint as subtitle_bp

blueprint = Blueprint.group(subtitle_bp, url_prefix='/admin')
