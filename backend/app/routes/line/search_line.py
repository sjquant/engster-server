from sanic.response import json

from ._line_bp import line_bp


@line_bp.route('/english/<keyword>', methods=['GET'])
async def search_english(request, keyword):
    """ search english """
    return json({
        "Hello": keyword
    })


@line_bp.route('/korean/<keyword>', methods=['GET'])
async def search_korean(request, keyword):
    """ search korean """
    return json({
        "안녕": keyword
    }, ensure_ascii=False)


@line_bp.route('/context/<line_id:int>', methods=['GET'])
async def search_context(request, line_id):
    """ search context """
    return json({
        "context를": '반환합니다.'
    }, ensure_ascii=False)
