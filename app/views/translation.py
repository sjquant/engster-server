from typing import Optional
from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic_jwt_extended.tokens import Token
from sanic_jwt_extended import jwt_required
from sanic.exceptions import ServerError

from app.db_models import User, Translation
from app.utils import calc_max_page
from app.utils.response import JsonResponse
from app.utils.views import APIView, DetailAPIView
from app.utils.validators import expect_query, expect_body
from app import db

blueprint = Blueprint("translation_blueprint", url_prefix="/translations")


class TranslationListView(APIView):
    @expect_query(page=(int, 1), line_id=(int, ...))
    async def get(self, request: Request, page: int, line_id: int):
        page_size = request.app.config.get("COMMENT_PAGE_SIZE", 10)

        if not line_id:
            raise ServerError("line_id is required.", status_code=422)

        max_page, count = await calc_max_page(page_size, Translation.line_id == line_id)

        offset = page_size * (page - 1)

        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "page": 0, "count": 0, "lines": []}, status=200
            )

        translations = (
            await Translation.load(translator=User)
            .query.where(Translation.line_id == line_id)
            .limit(page_size)
            .offset(offset)
            .gino.all()
        )

        resp = []
        for each in translations:
            try:
                translator = each.translator.nickname
            except AttributeError:
                translator = "Anonymous"
            resp.append({**each.to_dict(), "translator": translator})
        return JsonResponse(resp)

    @jwt_required
    @expect_body(line_id=(int, ...), translation=(str, ...))
    async def post(self, request: Request, token: Token):
        user_id = token.jwt_identity
        translation = await Translation(**request.json, translator_id=user_id).create()
        nickname = await User.select("nickname").where(User.id == user_id).gino.scalar()
        return JsonResponse(
            {**translation.to_dict(), "translator": nickname}, status=201
        )


class TranslationDetailView(DetailAPIView):
    async def get_object(self, translation_id: int, token: Optional[Token] = None):

        if token:
            user_id = token.jwt_identity
            translation = await Translation.query.where(
                db.and_(
                    Translation.id == translation_id,
                    Translation.translator_id == user_id,
                )
            ).gino.first()

        else:
            translation = await Translation.query.where(
                db.and_(Translation.id == translation_id)
            ).gino.first()
        if translation is None:
            raise ServerError("no such translation", status_code=404)
        return translation

    @jwt_required
    async def put(self, request: Request, translation_id: int, token: Token):
        return await super().put(request, translation_id=translation_id, token=token)

    @jwt_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        return await super().delete(request, translation_id=translation_id, token=token)


blueprint.add_route(TranslationListView.as_view(), "")
blueprint.add_route(TranslationDetailView.as_view(), "/<translation_id:int>")
