from typing import List, Dict, Any, Tuple

from sanic.request import Request
from sanic.blueprints import Blueprint
from sanic_jwt_extended import jwt_optional
from sanic_jwt_extended.tokens import Token

from app.db_models import LineLike, TranslationLike, Translation
from app.db_access.mypage import (
    get_user_activitiy_summary,
    fetch_user_liked_english_lines,
    fetch_user_liked_korean_lines,
    fetch_user_translations,
)
from app.db_access.subtitle import (
    get_like_count_per_english_line,
    get_like_count_per_korean_line,
    get_translation_count_per_line,
    get_genres_per_content,
    get_user_liked_english_lines,
    get_user_liked_korean_lines,
)
from app.libs.views import APIView
from app.utils import JsonResponse
from app.decorators import expect_query
from app.utils import calc_max_page

blueprint = Blueprint("mypage_blueprint", url_prefix="/my-page")


class UserActivitySummary(APIView):
    async def get(self, request: Request, user_id: str):
        resp = await get_user_activitiy_summary(user_id)
        return JsonResponse(resp, status=200)


class UserLikedEnglishLines(APIView):
    def _get_required_ids(self, lines: List[Dict[str, Any]]) -> Tuple[List[int]]:
        content_ids = []
        line_ids = []
        for each in lines:
            content_ids.append(each["content_id"])
            line_ids.append(each["id"])
        return content_ids, line_ids

    @jwt_optional
    @expect_query(page=(int, 1), per_page=(int, 15))
    async def get(
        self, request: Request, user_id: str, page: int, per_page: int, token: Token
    ):
        max_page, count = await calc_max_page(per_page, LineLike.user_id == user_id)
        offset = per_page * (page - 1)
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "count": 0, "page": 0, "data": []}, status=200
            )
        lines = await fetch_user_liked_english_lines(
            user_id, limit=per_page, offset=offset
        )
        content_ids, line_ids = self._get_required_ids(lines)
        like_count = await get_like_count_per_english_line(line_ids)
        translation_count = await get_translation_count_per_line(line_ids)
        genres = await get_genres_per_content(content_ids)
        user_id = token.identity if token else None
        user_liked = (
            await get_user_liked_english_lines(user_id, line_ids) if user_id else []
        )
        data = [
            {
                **line,
                "genres": genres[line["content_id"]],
                "like_count": like_count.get(line["id"], 0),
                "translation_count": translation_count.get(line["id"], 0),
                "user_liked": line["id"] in user_liked,
            }
            for line in lines
        ]
        resp = {
            "max_page": max_page,
            "page": page,
            "count": count,
            "data": data,
        }

        return JsonResponse(resp, status=200,)


class UserLikedKoreanLines(APIView):
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
    @expect_query(page=(int, 1), per_page=(int, 15))
    async def get(
        self, request: Request, user_id: str, page: int, per_page: int, token: Token
    ):
        max_page, count = await calc_max_page(
            per_page, TranslationLike.user_id == user_id
        )
        offset = per_page * (page - 1)
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "count": 0, "page": 0, "data": []}, status=200
            )
        translations = await fetch_user_liked_korean_lines(
            user_id, limit=per_page, offset=offset
        )
        content_ids, translation_ids, line_ids = self._get_required_ids(translations)
        genres = await get_genres_per_content(content_ids)
        like_count = await get_like_count_per_korean_line(translation_ids)
        translation_count = await get_translation_count_per_line(line_ids)
        user_id = token.identity if token else None
        user_liked = (
            await get_user_liked_korean_lines(user_id, translation_ids)
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
            {"max_page": max_page, "page": page, "count": count, "data": data},
            status=200,
        )


class UserTranslations(APIView):
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
    @expect_query(page=(int, 1), per_page=(int, 15))
    async def get(
        self, request: Request, user_id: str, page: int, per_page: int, token: Token
    ):
        max_page, count = await calc_max_page(per_page, Translation.user_id == user_id)
        offset = per_page * (page - 1)
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "count": 0, "page": 0, "data": []}, status=200
            )
        translations = await fetch_user_translations(
            user_id, limit=per_page, offset=offset
        )
        content_ids, translation_ids, line_ids = self._get_required_ids(translations)
        genres = await get_genres_per_content(content_ids)
        like_count = await get_like_count_per_korean_line(translation_ids)
        translation_count = await get_translation_count_per_line(line_ids)
        user_id = token.identity if token else None
        user_liked = (
            await get_user_liked_korean_lines(user_id, translation_ids)
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
            {"max_page": max_page, "page": page, "count": count, "data": data},
            status=200,
        )


blueprint.add_route(UserActivitySummary.as_view(), "/<user_id:uuid>/activity-summary")
blueprint.add_route(
    UserLikedEnglishLines.as_view(), "/<user_id:uuid>/liked-english-lines"
)
blueprint.add_route(
    UserLikedKoreanLines.as_view(), "/<user_id:uuid>/liked-korean-lines"
)
blueprint.add_route(UserTranslations.as_view(), "/<user_id:uuid>/translations")
