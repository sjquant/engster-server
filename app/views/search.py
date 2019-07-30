from typing import List, Dict, Any

from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint
from sanic_jwt_extended import jwt_optional
from sanic_jwt_extended.tokens import Token
from pydantic import constr

from app import db
from app.db_models import (
    Line,
    Translation,
    Content,
    Genre,
    Category,
    ContentXGenre,
    LineLike,
    TranslationLike,
)

from app.utils import calc_max_page
from app.utils.response import JsonResponse
from app.utils.validators import expect_query


blueprint = Blueprint("search_blueprint", url_prefix="search")


async def get_most_liked_translations(line_ids: List[int]) -> Dict[str, Dict[str, Any]]:
    """
    각 라인별로 가장 좋아요를 많이 받은 번역을 리턴

    params
    ----------
    line_ids: array-like-string
    """

    if not line_ids:
        raise ServerError("Nothing Found", status_code=404)

    query = f"""
        SELECT t2.id, t2.translation, t2.line_id FROM (
            SELECT t1.*, row_number()
            OVER (partition by t1.line_id
            ORDER BY t1.trans_like_count DESC) as rn
            FROM (
                SELECT translation.id, translation.translation,
                    translation.line_id,
                    count(translation_like.translation_id)
                    AS trans_like_count
                FROM translation LEFT OUTER JOIN translation_like
                ON translation.id = translation_like.translation_id
                GROUP BY translation.id
                HAVING translation.line_id IN {tuple(line_ids)}
            ) t1 ) t2
        WHERE t2.rn = 1
    """

    res = await db.status(query)
    data = {
        f"line_{each[2]}": {"id": each[0], "translation": each[1]} for each in res[1]
    }

    return data


async def get_genres_for_content(content_ids: List[int]) -> Dict[str, Dict[str, Any]]:
    """
    get genres of each content
    """

    query = (
        db.select([Genre.id, Genre.genre, ContentXGenre.content_id])
        .select_from(Genre.join(ContentXGenre))
        .where(ContentXGenre.content_id.in_(content_ids))
    )

    res = await query.gino.all()

    data: dict = {}
    for each in res:
        content = data.setdefault(f"content_{each[2]}", [])
        content.append({"id": each[0], "genre": each[1]})

    return data


async def get_english_like_count(line_ids: List[int]) -> Dict[int, int]:
    """ get like count for lines """
    query = (
        db.select([LineLike.line_id, db.func.count(LineLike.line_id)])
        .where(LineLike.line_id.in_(line_ids))
        .group_by(LineLike.line_id)
    )

    res = await query.gino.all()
    data = {each[0]: each[1] for each in res}
    return data


async def get_korean_like_count(translation_ids: List[int]) -> Dict[int, int]:
    """ get korean count for translations """
    query = (
        db.select(
            [
                TranslationLike.translation_id,
                db.func.count(TranslationLike.translation_id),
            ]
        )
        .where(TranslationLike.id.in_(translation_ids))
        .group_by(TranslationLike.translation_id)
    )

    res = await query.gino.all()
    data = {each[0]: each[1] for each in res}
    return data


async def get_user_liked_english_lines(user_id, line_ids: List[int]) -> List[int]:
    query = db.select([LineLike.line_id]).where(
        db.and_(LineLike.user_id == user_id, LineLike.line_id.in_(line_ids))
    )
    res = await query.gino.all()
    return [each[0] for each in res]


async def get_user_liked_korean_lines(user_id, translation_ids: List[int]) -> List[int]:
    query = db.select([TranslationLike.translation_id]).where(
        db.and_(
            TranslationLike.user_id == user_id,
            TranslationLike.translation_id.in_(translation_ids),
        )
    )
    res = await query.gino.all()
    return [each[0] for each in res]


async def get_translation_count(line_ids: List[int]) -> Dict[int, int]:
    query = (
        db.select([Translation.line_id, db.func.count(Translation.line_id)])
        .where(Translation.line_id.in_(line_ids))
        .group_by(Translation.line_id)
    )
    res = await query.gino.all()
    data = {each[0]: each[1] for each in res}
    return data


@blueprint.route("/english", methods=["GET"])
@jwt_optional
@expect_query(page=(int, 1), keyword=(constr(min_length=2), ...))
async def search_english(request, page: int, keyword: str, token: Token):
    """ search english """

    page_size = 10

    max_page, count = await calc_max_page(
        page_size, Line.line.op("~*")(keyword + r"[\.?, ]")
    )
    offset = page_size * (page - 1)

    if page > max_page:
        return JsonResponse(
            {"max_page": 0, "count": 0, "page": 0, "lines": [], "user_liked": []},
            status=200,
        )

    lines = (
        await Line.load(content=Content)
        .load(category=Category)
        .query.where(Line.line.op("~*")(keyword + r"[\.?, ]"))
        .limit(page_size)
        .offset(offset)
        .gino.all()
    )

    content_ids = []
    line_ids = []
    for each in lines:
        content_ids.append(each.content.id)
        line_ids.append(each.id)

    genres = await get_genres_for_content(content_ids)
    like_count = await get_english_like_count(line_ids)
    user_id = token.jwt_identity
    if user_id:
        user_liked = await get_user_liked_english_lines(user_id, line_ids)
    else:
        user_liked = []
    translation_count = await get_translation_count(line_ids)

    lines = [
        {
            **line.to_dict(["id", "line"]),
            **{"like_count": like_count.get(line.id, 0)},
            **{"translation_count": translation_count.get(line.id, 0)},
            **{"content": line.content.to_dict(["id", "title", "year"])},
            **{"category": line.category.to_dict()},
            **{"genres": genres[f"content_{line.content.id}"]},
        }
        for line in lines
    ]

    resp = {
        "max_page": max_page,
        "page": page,
        "count": count,
        "lines": lines,
        "user_liked": user_liked,
    }
    return JsonResponse(resp, status=200)


@blueprint.route("/korean", methods=["GET"])
@jwt_optional
@expect_query(page=(int, 1), keyword=(constr(min_length=2), ...))
async def search_korean(request, page: int, keyword: str, token: Token):
    """ search korean """

    page_size = 10

    max_page, count = await calc_max_page(
        page_size, Translation.translation.ilike("%" + keyword + "%")
    )
    offset = page_size * (page - 1)

    if page > max_page:
        return JsonResponse(
            {"max_page": 0, "page": 0, "count": 0, "lines": [], "user_liked": []},
            status=200,
        )

    translations = (
        await Translation.load(line=Line)
        .load(content=Content)
        .load(category=Category)
        .where(Translation.translation.ilike("%" + keyword + "%"))
        .limit(page_size)
        .offset(offset)
        .gino.all()
    )

    content_ids = []
    translation_ids = []
    line_ids = []

    for each in translations:
        content_ids.append(each.content.id)
        translation_ids.append(each.id)
        line_ids.append(each.line_id)

    genres = await get_genres_for_content(content_ids)
    like_count = await get_korean_like_count(translation_ids)
    user_id = token.jwt_identity
    if user_id:
        user_liked = await get_user_liked_english_lines(user_id, translation_ids)
    else:
        user_liked = []
    translation_count = await get_translation_count(line_ids)

    translations = [
        {
            **each.to_dict(show=["id", "translation"]),
            **{"line": each.line.to_dict(show=["id", "line"])},
            **{"like_count": like_count.get(each.id, 0)},
            **{"translation_count": translation_count.get(each.id, 0)},
            **{"content": each.content.to_dict(show=["id", "title", "year"])},
            **{"category": each.category.to_dict()},
            **{"genres": genres[f"content_{each.content.id}"]},
        }
        for each in translations
    ]

    resp = {
        "max_page": max_page,
        "page": page,
        "count": count,
        "lines": translations,
        "user_liked": user_liked,
    }

    return JsonResponse(resp)


@blueprint.route("/context/<content_id:int>/<line_id:int>", methods=["GET"])
async def search_context(request, content_id, line_id):
    """ search context """

    before_lines = (
        await Line.query.where(db.and_(Line.id <= line_id, Content.id == content_id))
        .limit(5)
        .order_by(Line.id.desc())
        .gino.all()
    )
    after_lines = (
        await Line.query.where(db.and_(Line.id > line_id, Content.id == content_id))
        .limit(5)
        .order_by(Line.id.asc())
        .gino.all()
    )

    lines = before_lines[::-1] + after_lines
    line_ids = [each.id for each in lines]

    translations = await get_most_liked_translations(line_ids)

    lines = [
        {
            **line.to_dict(["id", "line"]),
            **{"translation": translations[f"line_{line.id}"]},
        }
        for line in lines
    ]

    data = {"lines": lines}

    return JsonResponse(data, status=200)
