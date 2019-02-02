from sanic.response import json
from .blueprint import lines_bp


@lines_bp.route('search/english/<keyword>', methods=['GET'])
async def search_english(request, keyword):
    """ search english """
    return json({
        "Hello": keyword
    })


@lines_bp.route('search/korean/<keyword>', methods=['GET'])
async def search_korean(request, keyword):
    """ search korean """
    return json({
        "안녕": keyword
    }, ensure_ascii=False)


@lines_bp.route('search/context/<line_id:int>', methods=['GET'])
async def search_context(request, line_id):
    """ search context """
    return json({
        "context를": '반환합니다.'
    }, ensure_ascii=False)
