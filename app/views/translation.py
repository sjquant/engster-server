from typing import Optional
from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic_jwt_extended.tokens import Token
from sanic_jwt_extended import jwt_required, jwt_optional
from sanic.exceptions import ServerError

from app.db_models import User, Translation
from app.utils import calc_max_page
from app.utils import JsonResponse
from app.libs.views import APIView, DetailAPIView
from app.decorators import expect_query, expect_body
from app.loaders import get_korean_like_count, get_user_liked_korean_lines
from app import db

blueprint = Blueprint("translation_blueprint", url_prefix="/translations")


class TranslationListView(APIView):
    @jwt_optional
    @expect_query(page=(int, 1), line_id=(int, ...))
    async def get(self, request: Request, page: int, line_id: int, token: Token):
        page_size = request.app.config.get("COMMENT_PAGE_SIZE", 10)

        if not line_id:
            raise ServerError("line_id is required.", status_code=422)

        max_page, count = await calc_max_page(page_size, Translation.line_id == line_id)

        offset = page_size * (page - 1)

        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "page": 0, "count": 0, "translations": []}, status=200
            )

        translations = (
            await Translation.load(translator=User)
            .query.where(db.and_(Translation.line_id == line_id))
            .limit(page_size)
            .offset(offset)
            .gino.all()
        )
        translation_ids = []
        for each in translations:
            translation_ids.append(each.id)

        like_count = await get_korean_like_count(translation_ids)
        user_id = token.jwt_identity
        if user_id:
            user_liked = await get_user_liked_korean_lines(user_id, translation_ids)
        else:
            user_liked = []

        temp_resp = []

        for each in translations:
            try:
                translator = each.translator.nickname
            except AttributeError:
                translator = "Anonymous"
            temp_resp.append(
                {
                    **each.to_dict(),
                    "translator": translator,
                    "like_count": like_count.get(each.id, 0),
                    "user_liked": each.id in user_liked,
                }
            )

        resp = {
            "max_page": max_page,
            "page": page,
            "count": count,
            "translations": temp_resp,
        }

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
