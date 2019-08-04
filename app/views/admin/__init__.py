from sanic.blueprints import Blueprint

from .subtitle import blueprint as subtitle_bp
from .lines import blueprint as lines_bp

blueprint = Blueprint.group(subtitle_bp, lines_bp, url_prefix='/admin')
