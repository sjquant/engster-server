from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic_jwt_extended.tokens import Token
from sanic_jwt_extended import jwt_required
from sanic.exceptions import ServerError

from app.db_models import User, Translation
from app.utils import calc_max_page
from app.utils.serializer import jsonify
from app.utils.views import APIView
from app.utils.validators import validate_queries

blueprint = Blueprint('translation_blueprint', url_prefix='/translations')


class TranslationListView(APIView):

    @validate_queries(page=(int, 1), line_id=(int, ...))
    async def get(self, request: Request, page: int, line_id: int):
        page_size = request.app.config.get('COMMENT_PAGE_SIZE', 10)

        if not line_id:
            raise ServerError('line_id is required.', status_code=422)

        max_page, count = await calc_max_page(
            page_size, Translation.line_id == line_id)

        offset = page_size * (page - 1)

        if page > max_page:
            return jsonify({
                'max_page': 0,
                'page': 0,
                'count': 0,
                'lines': []
            })

        translations = await Translation.load(
            translator=User).query.where(
                Translation.line_id == line_id).limit(
                    page_size).offset(offset).gino.all()

        resp = []
        for each in translations:
            try:
                translator = each.translator.nickname
            except AttributeError:
                translator = 'Anonymous'
            resp.append(
                {
                    **each.to_dict(),
                    'translator': translator
                }
            )
        return jsonify(resp)

    @jwt_required
    async def post(self, request: Request, token: Token):
        user_id = token.jwt_identity
        translation = await Translation(
            **request.json, translator_id=user_id
        ).create()
        nickname = await User.select(
            'nickname').where(
                User.id == user_id).gino.scalar()
        return jsonify(
            {
                **translation.to_dict(),
                'translator': nickname
            },
            status=201
        )


blueprint.add_route(TranslationListView.as_view(), '')
