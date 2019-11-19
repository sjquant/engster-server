from sanic.request import Request
from sanic.blueprints import Blueprint

from app import db
from app.db_models import Line, LineLike, TranslationLike, Translation, Content, User
from app.utils.response import JsonResponse
from app.utils.validators import expect_query
from app.utils import calc_max_page

blueprint = Blueprint("mypage_blueprint", url_prefix="/my-page")


@blueprint.route("/<user_id:uuid>/activity-summary", methods=["GET"])
async def get_user_activitiy_summary(request: Request, user_id: str):
    query = (
        db.select([db.func.count(Translation.id)])
        .select_from(User.join(Translation))
        .where(User.id == user_id)
        .group_by(User.id)
    )
    resp = await query.gino.first()
    if resp is None:
        data = {"user_id": user_id, "translation_count": 0}
    else:
        data = {"user_id": user_id, "translation_count": resp[0]}
    return JsonResponse(data, status=200)


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
            "content": each.content.to_dict(show=["id", "title", "year"]),
        }
        for each in await query.gino.all()
    ]

    return JsonResponse(
        {"max_page": max_page, "page": page, "count": count, "lines": data}, status=200
    )


@blueprint.route("/<user_id:uuid>/line-likes/korean", methods=["GET"])
@expect_query(page=(int, 1))
async def get_korean_likes(request: Request, user_id: str, page: int):

    page_size = 10
    max_page, count = await calc_max_page(page_size, TranslationLike.user_id == user_id)
    offset = page_size * (page - 1)

    if page > max_page:
        return JsonResponse(
            {"max_page": 0, "count": 0, "page": 0, "lines": []}, status=200
        )

    query = (
        Translation.load(like=TranslationLike, line=Line, content=Content)
        .query.where(
            db.and_(
                Translation.id == TranslationLike.translation_id,
                Translation.line_id == Line.id,
                Line.content_id == Content.id,
            )
        )
        .limit(page_size)
        .offset(offset)
        .order_by(TranslationLike.created_at.desc())
    )

    data = [
        {
            **each.to_dict(show=["id", "translation", "line_id"]),
            "line": each.line.line,
            "liked_at": each.like.created_at,
            "content": each.content.to_dict(show=["id", "title", "year"]),
        }
        for each in await query.gino.all()
    ]

    return JsonResponse(
        {"max_page": max_page, "page": page, "count": count, "lines": data}, status=200
    )


@blueprint.route("/<user_id:uuid>/translations", methods=["GET"])
@expect_query(page=(int, 1))
async def get_translations(request: Request, user_id: str, page: int):
    page_size = 10
    max_page, count = await calc_max_page(
        page_size, Translation.translator_id == user_id
    )
    offset = page_size * (page - 1)
    #
    if page > max_page:
        return JsonResponse(
            {"max_page": 0, "count": 0, "page": 0, "lines": []}, status=200
        )

    query = (
        Translation.load(line=Line, content=Content)
        .query.where(
            db.and_(
                Translation.line_id == Line.id,
                Line.content_id == Content.id,
                Translation.translator_id == user_id,
            )
        )
        .limit(page_size)
        .offset(offset)
        .order_by(Translation.created_at.desc())
    )

    translations = await query.gino.all()

    translation_ids = []
    for each in translations:
        translation_ids.append(each.id)

    data = [
        {
            **each.to_dict(show=["id", "translation", "line_id"]),
            "line": each.line.line,
            "content": each.content.to_dict(show=["id", "title", "year"]),
        }
        for each in translations
    ]

    return JsonResponse(
        {"max_page": max_page, "page": page, "count": count, "lines": data}, status=200
    )
