from typing import List, Tuple, Dict, Any, Optional
from io import StringIO

from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic.blueprints import Blueprint
from sanic_jwt_extended import jwt_required
from sanic_jwt_extended.tokens import Token
from pydantic import constr

import asyncpg

from app.decorators import expect_query, expect_body
from app.core.sanic_jwt_extended import admin_required, jwt_optional
from app.services import translation as translation_service
from app.services import subtitle as subtitle_service
from app.services import content as content_service
from app.models import Translation
from app.utils import JsonResponse, csv_to_dict

blueprint = Blueprint("translation_blueprint", url_prefix="translations")


class AddTranslationCSV(HTTPMethodView):
    async def _upload_translation(self, data):
        translations = [
            {"translation": trans, "line_id": int(line_id)}
            for trans, line_id in zip(data["translation"], data["line_id"])
        ]
        await Translation.insert().gino.all(translations)

    @admin_required
    async def post(self, request: Request, token: Token):
        input_file = request.files.get("file")
        data = csv_to_dict(StringIO(input_file.body.decode("utf-8-sig")))

        if "line_id" not in data.keys():
            return JsonResponse({"message": "line_id field not found"}, status=400)

        await self._upload_translation(data)
        return JsonResponse({"message": "success"})


class TranslationDetail(HTTPMethodView):
    async def get(self, request, translation_id: int):
        translation = await translation_service.get_by_id(translation_id)
        if not translation:
            return JsonResponse({"message": "Translation not found"}, status=404)
        return JsonResponse(translation.to_dict(), 200)

    @jwt_required
    @expect_body(translation=(str, ...))
    async def patch(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        is_admin = token.role == "admin"
        trans = request.json["translation"]

        translation = await translation_service.get_by_id(translation_id)
        if not translation:
            return JsonResponse({"message": "Translation not found"}, status=404)

        if translation.user_id != user_id:
            return JsonResponse({"message": "Permission Denied"}, status=403)

        status = "APPROVED" if is_admin else "PENDING"

        await translation.update(translation=trans, status=status).apply()
        return JsonResponse({"message": "success"}, status=200)

    @jwt_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity

        translation = await translation_service.get_by_id(translation_id)
        if not translation:
            return JsonResponse({"message": "Translation not found"}, status=404)

        if translation.user_id != user_id:
            return JsonResponse({"message": "Permission Denied"}, status=403)

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
        self,
        request,
        limit: int,
        cursor: Optional[int],
        keyword: str,
        token: Optional[Token],
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
        resp = {"cursor": cursor, "count": count, "data": data}
        return JsonResponse(resp)


class LikeTranslation(HTTPMethodView):
    @jwt_required
    async def post(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        try:
            await translation_service.add_like(translation_id, user_id)
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "Already liked"}, status=400)
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
        self,
        request: Request,
        user_id: str,
        limit: int,
        cursor: Optional[int],
        token: Token,
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
            {"limit": limit, "cursor": cursor, "data": data}, status=200
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
        self,
        request: Request,
        user_id: str,
        limit: int,
        cursor: Optional[int],
        token: Token,
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
            {"limit": limit, "cursor": cursor, "data": data}, status=200
        )


class TranslationChangeStatusView(HTTPMethodView):
    @admin_required
    @expect_body(status=(str, ...), message=(str, None))
    async def post(self, request: Request, translation_id: int, token: Token):
        status = request.json["status"]
        message = request.json["message"]
        reviewer_id = token.identity
        try:
            await translation_service.change_status(
                translation_id, status, reviewer_id, message
            )
        except ValueError as e:
            return JsonResponse({"message": str(e)}, status=400)
        return JsonResponse({"message": "success"}, status=200)


class TranslationReviewList(HTTPMethodView):
    @admin_required
    @expect_query(limit=(int, 20), cursor=(int, None))
    async def get(
        self,
        request: Request,
        translation_id: int,
        limit: int,
        cursor: Optional[int],
        token: Token,
    ):

        count = (
            await translation_service.count_reviews(translation_id)
            if cursor is None
            else None
        )
        data = await translation_service.fetch_reviews(translation_id, limit, cursor)
        return JsonResponse(
            {"count": count, "data": data, "cursor": cursor, "limit": limit}
        )


blueprint.add_route(SearchTranslation.as_view(), "/search")
blueprint.add_route(AddTranslationCSV.as_view(), "/add-csv")
blueprint.add_route(UserLikedTranslations.as_view(), "/liked")
blueprint.add_route(UserWrittenTranslations.as_view(), "/written")
blueprint.add_route(TranslationDetail.as_view(), "/<translation_id:int>")
blueprint.add_route(LikeTranslation.as_view(), "/<translation_id:int>/like")
blueprint.add_route(
    TranslationChangeStatusView.as_view(), "/<translation_id:int>/change-status"
)
blueprint.add_route(TranslationReviewList.as_view(), "/<translation_id:int>/reviews")
