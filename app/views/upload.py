from sanic.request import Request
from sanic.blueprints import Blueprint

from app import db
from app.db_models import Line, LineLike, TranslationLike, Translation, Content, User
from app.utils.response import JsonResponse
from app.utils.validators import expect_query
from app.utils import calc_max_page

blueprint = Blueprint("common_blueprint", url_prefix="/common")


@blueprint.route("/upload-photo", methods=["POST"]):
async def upload_photo(request: Request):
    pass