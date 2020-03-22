from sanic.request import Request
from sanic.blueprints import Blueprint

from app import db
from app.db_models import Line, LineLike, TranslationLike, Translation, Content, User
from app.db_access.mypage import (
    get_user_activitiy_summary,
    fetch_user_liked_english_lines,
    fetch_user_liked_korean_lines,
    fetch_user_translations,
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
    @expect_query(page=(int, 1), per_page=(int, 15))
    async def get(self, request: Request, user_id: str, page: int, per_page: int):
        max_page, count = await calc_max_page(per_page, LineLike.user_id == user_id)
        offset = per_page * (page - 1)
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "count": 0, "page": 0, "data": []}, status=200
            )
        data = await fetch_user_liked_english_lines(
            user_id, limit=per_page, offset=offset
        )

        return JsonResponse(
            {"max_page": max_page, "page": page, "count": count, "data": data},
            status=200,
        )


class UserLikedKoreanLines(APIView):
    @expect_query(page=(int, 1), per_page=(int, 15))
    async def get(self, request: Request, user_id: str, page: int, per_page: int):
        max_page, count = await calc_max_page(
            per_page, TranslationLike.user_id == user_id
        )
        offset = per_page * (page - 1)
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "count": 0, "page": 0, "data": []}, status=200
            )
        data = await fetch_user_liked_korean_lines(
            user_id, limit=per_page, offset=offset
        )
        return JsonResponse(
            {"max_page": max_page, "page": page, "count": count, "data": data},
            status=200,
        )


class UserTranslations(APIView):
    @expect_query(page=(int, 1), per_page=(int, 15))
    async def get(self, request: Request, user_id: str, page: int, per_page: int):
        max_page, count = await calc_max_page(per_page, Translation.user_id == user_id)
        offset = per_page * (page - 1)
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "count": 0, "page": 0, "data": []}, status=200
            )
        data = await fetch_user_translations(user_id, limit=per_page, offset=offset)
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
