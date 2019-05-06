from typing import List, Dict, Any

from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint

from app import db
from app.models import (
    Line,
    Translation,
    Content,
    Genre,
    Category,
    ContentXGenre,
    LineLike,
    TranslationLike
)

from app.utils import calc_max_page
from app.utils.serializer import jsonify

page_size = 10
blueprint = Blueprint('search_blueprint', url_prefix='search')


async def get_most_liked_translations(
        line_ids: List[int]) -> Dict[str, Dict[str, Any]]:
    """
    각 라인별로 가장 좋아요를 많이 받은 번역을 리턴

    params
    ----------
    line_ids: array-like-string
    """

    if not line_ids:
        raise ServerError('Nothing Found', status_code=404)

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
        f'line_{each[2]}': {
            'id': each[0],
            'translation': each[1]
        }
        for each in res[1]
    }

    return data


async def get_genres_for_content(
        content_ids: List[int]) -> Dict[str, Dict[str, Any]]:
    """
    해당 id를 가진 genres를 리턴
    """

    query = db.select(
        [Genre.id, Genre.genre, ContentXGenre.content_id]
    ).select_from(
        Genre.join(ContentXGenre)
    ).where(
        ContentXGenre.content_id.in_(content_ids)
    )

    res = await query.gino.all()

    data: dict = {}
    for each in res:
        content = data.setdefault(f'content_{each[2]}', [])
        content.append({
            'id': each[0],
            'genre': each[1]
        })

    return data


async def get_english_like_count(line_ids: List[int]) -> Dict[int, int]:
    """ get like count for lines """
    query = db.select([
        LineLike.line_id, db.func.count(LineLike.line_id)
    ]).where(
        LineLike.line_id.in_(line_ids)
    ).group_by(LineLike.line_id)

    res = await query.gino.all()
    data = {each[0]: each[1] for each in res}
    return data


async def get_korean_like_count(translation_ids: List[int]) -> Dict[int, int]:
    """ get korean count for translations """
    query = db.select([
        TranslationLike.translation_id,
        db.func.count(TranslationLike.translation_id)
    ]).where(
        TranslationLike.id.in_(translation_ids)
    ).group_by(TranslationLike.translation_id)

    res = await query.gino.all()
    data = {each[0]: each[1] for each in res}
    return data


async def get_translation_count(line_ids: List[int]) -> Dict[int, int]:
    query = db.select([
        Translation.line_id,
        db.func.count(Translation.line_id)
    ]).where(
        Translation.line_id.in_(line_ids)
    ).group_by(Translation.line_id)
    res = await query.gino.all()
    data = {each[0]: each[1] for each in res}
    return data


@blueprint.route('/english', methods=['GET'])
async def search_english(request):
    """ search english """

    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', '')

    if len(keyword) < 2:
        raise ServerError(
            "keyword length must be greater than 2", status_code=400)

    max_page = await calc_max_page(
        page_size, Line.line.op('~*')(keyword+r'[\.?, ]'))
    offset = page_size * (page - 1)

    if page > max_page:
        return jsonify({
            'max_page': 0,
            'page': 0,
            'lines': []
        })

    lines = await Line.load(
        content=Content).load(
            category=Category).query.where(
        Line.line.op('~*')(keyword+r'[\.?, ]')
    ).limit(page_size).offset(offset).gino.all()

    content_ids = []
    line_ids = []
    for each in lines:
        content_ids.append(each.content.id)
        line_ids.append(each.id)

    genres = await get_genres_for_content(content_ids)
    like_count = await get_english_like_count(line_ids)
    translation_count = await get_translation_count(line_ids)

    lines = [
        {
            **line.to_dict(['id', 'line']),
            **{'like_count': like_count.get(line.id, 0)},
            **{'translation_count': translation_count.get(line.id, 0)},
            **{'content': line.content.to_dict(['id', 'title'])},
            **{'category': line.category.to_dict()},
            **{'genres': genres[f'content_{line.content.id}']}
        } for line in lines
    ]

    resp = {
        'max_page': max_page,
        'page': page,
        'lines': lines,
    }
    return jsonify(resp, ensure_ascii=False)


@blueprint.route('/korean', methods=['GET'])
async def search_korean(request):
    """ search korean """

    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', '')
    if len(keyword) < 2:
        raise ServerError(
            'keyword length must be greater than 2', status_code=400)

    max_page = await calc_max_page(
        page_size, Translation.translation.ilike('%'+keyword+'%'))
    offset = page_size * (page - 1)

    if page > max_page:
        return jsonify({
            'max_page': 0,
            'page': 0,
            'lines': []
        })

    translations = await Translation.load(
        line=Line).load(content=Content).load(category=Category).where(
        Translation.translation.ilike(
            '%'+keyword+'%')).limit(page_size).offset(offset).gino.all()

    content_ids = []
    translation_ids = []
    line_ids = []

    for each in translations:
        content_ids.append(each.content.id)
        translation_ids.append(each.id)
        line_ids.append(each.line_id)

    genres = await get_genres_for_content(content_ids)
    like_count = await get_korean_like_count(translation_ids)
    translation_count = await get_translation_count(line_ids)

    translations = [{
        **each.to_dict(show=['id', 'translation']),
        **{'line': each.line.to_dict(show=['id', 'line'])},
        **{'like_count': like_count.get(each.id, 0)},
        **{'translation_count': translation_count.get(each.id, 0)},
        **{'content': each.content.to_dict(show=['id', 'title'])},
        **{'category': each.category.to_dict()},
        **{'genres':  genres[f'content_{each.content.id}']}
    } for each in translations]

    resp = {
        'max_page': max_page,
        'page': page,
        'lines': translations,
    }

    return jsonify(resp, ensure_ascii=False)


@blueprint.route('/context/<content_id:int>/<line_id:int>', methods=['GET'])
async def search_context(request, content_id, line_id):
    """ search context """

    before_lines = await Line.query.where(
        db.and_(Line.id <= line_id, Content.id == content_id)
    ).limit(5).order_by(Line.id.desc()).gino.all()
    after_lines = await Line.query.where(
        db.and_(Line.id > line_id, Content.id == content_id)
    ).limit(5).order_by(Line.id.asc()).gino.all()

    lines = before_lines[::-1] + after_lines
    line_ids = [each.id for each in lines]

    translations = await get_most_liked_translations(line_ids)

    lines = [
        {
            **line.to_dict(['id', 'line']),
            **{
                'translation': translations[f'line_{line.id}']
            }
        } for line in lines
    ]

    data = {
        'lines': lines,
    }

    return jsonify(data, ensure_ascii=False)
