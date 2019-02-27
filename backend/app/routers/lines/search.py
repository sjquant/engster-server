from sanic.response import json
from sanic.exceptions import ServerError

from .blueprint import lines_bp
from app import models, db
from app.utils import calc_max_page
from app.utils.serializers import jsonify

page_size = 10


@lines_bp.route('/search/english/<keyword>', methods=['GET'])
async def search_english(request, keyword: str):
    """ search english """

    page = int(request.args.get('page', 1))

    if len(keyword) < 2:
        raise ServerError(
            "Keyword length must be greater than 2", status_code=400)

    line = models.Line

    max_page = await calc_max_page(page_size, line.line.ilike('%'+keyword+'%'))

    if page > max_page:
        raise ServerError("Nothing Found", status_code=404)

    lines = await line.query.where(line.line.ilike('%'+keyword+'%')).limit(page_size).offset(page).gino.all()
    lines = [each.to_dict() for each in lines]

    data = {
        'max_page': max_page,
        'page': page,
        'lines': lines,
    }
    return jsonify(data)


@lines_bp.route('/search/korean/<keyword>', methods=['GET'])
async def search_korean(request, keyword):
    """ search korean """

    page = int(request.args.get('page', 1))

    if len(keyword) < 2:
        raise ServerError(
            "Keyword length must be greater than 2", status_code=400)

    translation = models.Translation
    line = models.Line

    max_page = await calc_max_page(page_size, translation.translation.ilike('%'+keyword+'%'))
    if page > max_page:
        raise ServerError("Nothing Found", status_code=404)

    translations = await translation.load(line=line).where(
        translation.translation.ilike('%'+keyword+'%')).gino.all()

    data = []
    for each in translations:
        data.append({**each.to_dict(), **{'line': each.line.to_dict()}})

    return jsonify(data, ensure_ascii=False)


@lines_bp.route('/search/context/<line_id:int>', methods=['GET'])
async def search_context(request, line_id):
    """ search context """
    return jsonify({
        "context를": '반환합니다.'
    }, ensure_ascii=False)
