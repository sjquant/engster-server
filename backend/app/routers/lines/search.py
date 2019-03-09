from typing import List
import json

from sanic.exceptions import ServerError

from .blueprint import lines_bp
from app import models, db
from app.utils import calc_max_page
from app.utils.serializer import jsonify

page_size = 10


async def get_most_liked_translations(line_ids: List[int]):
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
            SELECT t1.*, row_number() over (partition by t1.line_id ORDER BY t1.trans_like_count DESC) as rn
            FROM (
                SELECT translation.id, translation.translation,
                    translation.line_id, count(translation_like.translation_id) AS trans_like_count
                FROM translation LEFT OUTER JOIN translation_like ON translation.id = translation_like.translation_id
                    GROUP BY translation.id HAVING translation.line_id IN {tuple(line_ids)}
            ) t1 ) t2
        WHERE t2.rn = 1
    """

    res = await db.status(query)
    data = {f'line_{each[2]}': {'id': each[0], 'translation': each[1]}
            for each in res[1]}

    return data


async def get_genres_for_content(content_ids: List[int]):
    """
    해당 id를 가진 genres를 리턴
    """
    genre = models.Genre
    contentXgenre = models.ContentXGenre

    query = db.select(
        [genre.id, genre.genre, contentXgenre.content_id]
    ).select_from(
        genre.join(contentXgenre)
    ).where(
        contentXgenre.content_id.in_(content_ids)
    )

    res = await query.gino.all()

    data = {}
    for each in res:
        content = data.setdefault(f'content_{each[2]}', [])
        content.append({
            'id': each[0],
            'genres': each[1]
        })

    return data


@lines_bp.route('/search/english/<keyword>', methods=['GET'])
async def search_english(request, keyword: str):
    """ search english """

    line = models.Line
    content = models.Content
    page = int(request.args.get('page', 1))

    if len(keyword) < 2:
        raise ServerError(
            "Keyword length must be greater than 2", status_code=400)

    max_page = await calc_max_page(page_size, line.line.op('~*')(keyword+r'[\.?, ]'))

    if page > max_page:
        raise ServerError("Nothing Found", status_code=404)

    lines = await line.load(content=content).query.where(
        line.line.op('~*')(keyword+r'[\.?, ]')
    ).limit(page_size).offset(page).gino.all()

    line_ids = []
    content_ids = []
    for each in lines:
        line_ids.append(each.id)
        content_ids.append(each.content.id)

    translations = await get_most_liked_translations(line_ids)
    genres = await get_genres_for_content(content_ids)

    lines = [
        {
            **line.to_dict(['id', 'line']),
            **{
                'translation': translations[f'line_{line.id}']
            },
            **{'content': line.content.to_dict(['id', 'title'])},
            **{'genre': genres[f'content_{line.content.id}']}
        } for line in lines
    ]

    data = {
        'max_page': max_page,
        'page': page,
        'lines': lines,
    }
    return jsonify(data, ensure_ascii=False)


@lines_bp.route('/search/korean/<keyword>', methods=['GET'])
async def search_korean(request, keyword: str):
    """ search korean """

    page = int(request.args.get('page', 1))

    if len(keyword) < 2:
        raise ServerError(
            "Keyword length must be greater than 2", status_code=400)

    translation = models.Translation
    line = models.Line
    content = models.Content

    max_page = await calc_max_page(page_size, translation.translation.ilike('%'+keyword+'%'))
    if page > max_page:
        raise ServerError("Nothing Found", status_code=404)

    translations = await translation.load(line=line).load(content=content).where(
        translation.translation.ilike('%'+keyword+'%')).gino.all()

    content_ids = [each.content.id for each in translations]

    genres = await get_genres_for_content(content_ids)
    translations = [{
        **each.to_dict(show=['id', 'translation']),
        **{
            'line': each.line.to_dict(show=['id', 'line'])
        },
        **{
            'content': each.content.to_dict(show=['id', 'title'])
        },
        **{
            'genres':  genres[f'content_{each.content.id}']
        }
    } for each in translations]

    data = {
        'max_page': max_page,
        'page': page,
        'lines': translations,
    }
    return jsonify(data, ensure_ascii=False)


@lines_bp.route('/search/context/<line_id:int>', methods=['GET'])
async def search_context(request, line_id):
    """ search context """
    return jsonify({
        "context를": '반환합니다.'
    }, ensure_ascii=False)
