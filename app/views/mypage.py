from sanic.request import Request
from sanic.blueprints import Blueprint

from app.db_models import Line, LineLike, Content
from app.utils.response import JsonResponse
from app.utils.validators import expect_query
from app.utils import calc_max_page


blueprint = Blueprint("mypage_blueprint", url_prefix="/my-page")


@blueprint.route("/<user_id:uuid>/line-likes/english", methods=["GET"])
@expect_query(page=(int, 1))
async def get_english_likes(request: Request, user_id: str, page: int):

    page_size = 10
    max_page, count = await calc_max_page(page_size, LineLike.user_id == user_id)
    offset = page_size * (page - 1)

    if page > max_page:
        return JsonResponse(
            {"max_page": 0, "count": 0, "page": 0, "lines": []}, status=200
        )

    query = (
        Line.load(content=Content, like=LineLike)
        .query.where(Line.id == LineLike.line_id)
        .limit(page_size)
        .offset(offset)
        .order_by(LineLike.created_at.desc())
    )

    data = [
        {
            **each.to_dict(),
            "liked_at": each.like.created_at,
            "content": each.content.to_dict(show=["id", "title"]),
        }
        for each in await query.gino.all()
    ]

    return JsonResponse(
        {"max_page": max_page, "page": page, "count": count, "lines": data}, status=200
    )
