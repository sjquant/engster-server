from typing import List, Tuple, Dict, Any, Optional
from io import BytesIO

from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic.blueprints import Blueprint
from sanic.exceptions import ServerError
from sanic_jwt_extended import jwt_required, jwt_optional
from sanic_jwt_extended.tokens import Token
from pydantic import constr

import pandas as pd
import asyncpg

from app.decorators import expect_query, self_required, admin_required
from app.services import translation as translation_service
from app.services import subtitle as subtitle_service
from app.services import content as content_service
from app.models import Translation
from app.utils import JsonResponse

blueprint = Blueprint("translation_blueprint", url_prefix="translations")


class TranslationList(HTTPMethodView):
    async def _upload_translation(self, df):
        translation = df[["translation", "line_id"]]
        translations = translation.to_dict(orient="records")
        await Translation.insert().gino.all(translations)

    @admin_required
    @expect_query(content_id=(int, ...))
    async def post(self, request: Request, content_id: int, token: Token):
        content = await content_service.get_by_id(content_id)
        if content is None:
            raise ServerError("No Such Instance", status_code=404)

        input_file = request.files.get("input")
        data = BytesIO(input_file.body)
        df = pd.read_csv(data, encoding="utf-8")

        if "line_id" not in df.columns:
            raise ServerError(
                "line_id field is not found in given csv.", status_code=400
            )

        await self._upload_translation(df)
        return JsonResponse({"message": "success"})


class TranslationDetail(HTTPMethodView):
    async def get(self, request, translation_id: int):
        translation = await translation_service.get_by_id(translation_id)
        if not translation:
            raise ServerError("no such translation", 404)
        return JsonResponse(translation.to_dict(), 200)

    @self_required
    async def patch(self, request: Request, translation_id: int, token: Token):
        translation = await translation_service.get_by_id(translation_id)
        if not translation:
            raise ServerError("no such translation", 404)
        await translation.update(**request.json).apply()
        return JsonResponse({"message": "success"}, status=202)

    @self_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        translation = await translation_service.get_by_id(translation_id)
        if not translation:
            raise ServerError("no such translation", 404)
        await translation.delete()
        return JsonResponse({"message": "success"}, status=204)


class SearchTranslation(HTTPMethodView):
    def _get_required_ids(self, translations: List[Dict[str, Any]]) -> Tuple[List[int]]:
        content_ids = []
        translation_ids = []
        line_ids = []
        for each in translations:
            content_ids.append(each["content_id"])
            translation_ids.append(each["id"])
            line_ids.append(each["line_id"])
        return content_ids, translation_ids, line_ids

    @jwt_optional
    @expect_query(
        limit=(int, 20), cursor=(int, None), keyword=(constr(min_length=2), ...)
    )
    async def get(
        self, request, limit: int, cursor: int, keyword: str, token: Optional[Token]
    ):
        """search korean(translations)"""
        count = await translation_service.count(keyword) if cursor is None else None
        if count == 0:
            return JsonResponse({"data": [], "count": 0, "cursor": cursor})

        translations = await translation_service.search(keyword, limit, cursor)
        content_ids, translation_ids, line_ids = self._get_required_ids(translations)
        genres = await content_service.fetch_genres(content_ids)
        like_count = await translation_service.get_like_count(translation_ids)
        translation_count = await subtitle_service.fetch_translation_count(line_ids)
        user_id = token.identity if token else None
        user_liked = (
            await translation_service.pick_user_liked(user_id, translation_ids)
            if user_id
            else []
        )
        data = [
            {
                **each,
                "like_count": like_count.get(each["id"], 0),
                "translation_count": translation_count.get(each["line_id"], 0),
                "genres": genres[each["content_id"]],
                "user_liked": each["id"] in user_liked,
            }
            for each in translations
        ]
        resp = {
            "cursor": cursor,
            "count": count,
            "data": data,
        }
        return JsonResponse(resp)


class LikeTranslation(HTTPMethodView):
    @jwt_required
    async def post(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        try:
            await translation_service.add_like(translation_id, user_id)
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "already liked"}, status=400)
        return JsonResponse({"message": "liked"}, status=201)

    @jwt_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        await translation_service.remove_like(translation_id, user_id)
        return JsonResponse({"message": "deleted like"}, status=204)


class UserLikedTranslations(HTTPMethodView):
    def _get_required_ids(self, translations: List[Dict[str, Any]]) -> Tuple[List[int]]:
        content_ids = []
        translation_ids = []
        line_ids = []
        for each in translations:
            content_ids.append(each["content_id"])
            translation_ids.append(each["id"])
            line_ids.append(each["line_id"])
        return content_ids, translation_ids, line_ids

    @jwt_optional
    @expect_query(user_id=(str, ...), limit=(int, 20), cursor=(int, None))
    async def get(
        self, request: Request, user_id: str, limit: int, cursor: int, token: Token
    ):
        translations = await translation_service.fetch_user_liked(
            user_id, limit=limit, cursor=cursor
        )
        content_ids, translation_ids, line_ids = self._get_required_ids(translations)
        genres = await content_service.fetch_genres(content_ids)
        like_count = await translation_service.get_like_count(translation_ids)
        translation_count = await subtitle_service.fetch_translation_count(line_ids)
        user_id = token.identity if token else None
        user_liked = (
            await translation_service.pick_user_liked(user_id, translation_ids)
            if user_id
            else []
        )
        data = [
            {
                **each,
                "like_count": like_count.get(each["id"], 0),
                "translation_count": translation_count.get(each["line_id"], 0),
                "genres": genres[each["content_id"]],
                "user_liked": each["id"] in user_liked,
            }
            for each in translations
        ]

        return JsonResponse(
            {"limit": limit, "cursor": cursor, "data": data}, status=200,
        )


class UserWrittenTranslations(HTTPMethodView):
    def _get_required_ids(self, translations: List[Dict[str, Any]]) -> Tuple[List[int]]:
        content_ids = []
        translation_ids = []
        line_ids = []
        for each in translations:
            content_ids.append(each["content_id"])
            translation_ids.append(each["id"])
            line_ids.append(each["line_id"])
        return content_ids, translation_ids, line_ids

    @jwt_optional
    @expect_query(user_id=(str, ...), limit=(int, 20), cursor=(int, None))
    async def get(
        self, request: Request, user_id: str, limit: int, cursor: int, token: Token
    ):
        translations = await translation_service.fetch_user_written(
            user_id, limit=limit, cursor=cursor
        )
        content_ids, translation_ids, line_ids = self._get_required_ids(translations)
        genres = await content_service.fetch_genres(content_ids)
        like_count = await translation_service.get_like_count(translation_ids)
        translation_count = await subtitle_service.fetch_translation_count(line_ids)
        user_id = token.identity if token else None
        user_liked = (
            await translation_service.pick_user_liked(user_id, translation_ids)
            if user_id
            else []
        )
        data = [
            {
                **each,
                "like_count": like_count.get(each["id"], 0),
                "translation_count": translation_count.get(each["line_id"], 0),
                "genres": genres[each["content_id"]],
                "user_liked": each["id"] in user_liked,
            }
            for each in translations
        ]

        return JsonResponse(
            {"limit": limit, "cursor": cursor, "data": data}, status=200,
        )


blueprint.add_route(TranslationList.as_view(), "")
blueprint.add_route(SearchTranslation.as_view(), "/search")
blueprint.add_route(UserLikedTranslations.as_view(), "/liked")
blueprint.add_route(UserWrittenTranslations.as_view(), "/written")
blueprint.add_route(TranslationDetail.as_view(), "/<translation_id:int>")
blueprint.add_route(LikeTranslation.as_view(), "/<translation_id:int>/like")
