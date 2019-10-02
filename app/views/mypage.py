from sanic.request import Request
from sanic.blueprints import Blueprint

# from sanic_jwt_extended import jwt_optional
# from sanic_jwt_extended.tokens import Token

from app.db_models import LineLike
from app.utils.response import JsonResponse
from app.utils.validators import expect_query

blueprint = Blueprint("mypage_blueprint", url_prefix="/my-page")


@blueprint.route("/<user_id:uuid>/line-likes/english", methods=["GET"])
@expect_query(page=(int, 1))
async def get_english_likes(request: Request, user_id: str, page: int):
    likes = await LineLike.query.where(LineLike.user_id == user_id).gino.all()
    resp = [each.to_dict() for each in likes]
    return JsonResponse(resp, status=200)
