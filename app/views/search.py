from typing import List, Dict, Any

from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint
from pydantic import constr

from app import db
from app.db_models import Line, Translation, Content

from app.utils import calc_max_page
from app.utils import JsonResponse
from app.decorators import expect_query
from app.db_access.line import (
    get_like_count_per_korean_line,
    get_like_count_per_english_line,
    search_english_lines,
    search_korean_lines,
    get_translation_count_per_line,
    get_genres_per_content,
)


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


@blueprint.route("/english", methods=["GET"])
@expect_query(page=(int, 1), per_page=(int, 10), keyword=(constr(min_length=2), ...))
async def search_english(request, page: int, per_page: int, keyword: str):
    """search english"""
    max_page, count = await calc_max_page(
        per_page, Line.line.op("~*")(keyword + r"[\.?, ]")
    )
    if page > max_page:
        return JsonResponse(
            {"max_page": 0, "count": 0, "page": 0, "lines": [], "user_liked": []},
            status=200,
        )
    offset = per_page * (page - 1)
    lines = await search_english_lines(keyword, per_page, offset)
    content_ids = []
    line_ids = []
    for each in lines:
        content_ids.append(each["content_id"])
        line_ids.append(each["id"])
    like_count = await get_like_count_per_english_line(line_ids)
    translation_count = await get_translation_count_per_line(line_ids)
    genres = await get_genres_per_content(content_ids)
    lines = [
        {
            **line,
            "genres": genres[line["content_id"]],
            "like_count": like_count.get(line["id"], 0),
            "translation_count": translation_count.get(line["id"], 0),
        }
        for line in lines
    ]
    resp = {
        "max_page": max_page,
        "page": page,
        "count": count,
        "data": lines,
    }
    return JsonResponse(resp, status=200)


@blueprint.route("/korean", methods=["GET"])
@expect_query(page=(int, 1), per_page=(int, 10), keyword=(constr(min_length=2), ...))
async def search_korean(request, page: int, per_page: int, keyword: str):
    """search korean(translations)"""
    max_page, count = await calc_max_page(
        per_page, condition=Translation.translation.ilike("%" + keyword + "%")
    )
    offset = per_page * (page - 1)
    if page > max_page:
        return JsonResponse(
            {"max_page": 0, "page": 0, "count": 0, "lines": []}, status=200,
        )
    translations = await search_korean_lines(keyword, per_page, offset)
    content_ids = []
    translation_ids = []
    line_ids = []
    for each in translations:
        content_ids.append(each["content_id"])
        translation_ids.append(each["id"])
        line_ids.append(each["line_id"])

    genres = await get_genres_per_content(content_ids)
    like_count = await get_like_count_per_korean_line(translation_ids)
    translation_count = await get_translation_count_per_line(line_ids)
    translations = [
        {
            **each,
            "like_count": like_count.get(each["id"], 0),
            "translation_count": translation_count.get(each["id"], 0),
            "genres": genres[each["content_id"]],
        }
        for each in translations
    ]
    resp = {
        "max_page": max_page,
        "page": page,
        "count": count,
        "data": translations,
    }

    return JsonResponse(resp)


@blueprint.route("/context/<content_id:int>/<line_id:int>", methods=["GET"])
async def search_context(request, content_id: int, line_id: int):
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
        {**line.to_dict(["id", "line"]), "translation": translations[f"line_{line.id}"]}
        for line in lines
    ]

    data = {"lines": lines}

    return JsonResponse(data, status=200)
