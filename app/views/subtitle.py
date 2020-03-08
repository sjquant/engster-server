from typing import List, Tuple, Dict, Any, Optional

import asyncpg
from pydantic import constr
from sanic.request import Request
from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint
from sanic_jwt_extended import jwt_required, jwt_optional
from sanic_jwt_extended.tokens import Token

from app import db
from app.db_models import (
    User,
    Line,
    Translation,
    Category,
    Genre,
    Content,
    LineLike,
    TranslationLike,
)
from app.libs.views import APIView, ListAPIView, DetailAPIView
from app.libs.view_mixins import (
    UpdateModelMixin,
    DestroyModelMixin,
)
from app.utils import calc_max_page
from app.utils import JsonResponse
from app.decorators import expect_query, expect_body
from app.db_access.subtitle import (
    get_like_count_per_korean_line,
    get_like_count_per_english_line,
    randomly_pick_subtitles,
    search_english_lines,
    search_korean_lines,
    get_translation_count_per_line,
    get_genres_per_content,
    get_user_liked_english_lines,
    get_user_liked_korean_lines,
    get_translations,
    get_translation,
    create_english_like,
    delete_english_like,
    create_korean_like,
    delete_korean_like,
)


blueprint = Blueprint("subtitle_blueprint", url_prefix="subtitle")


class ContentList(ListAPIView):
    model = Content


class CategoryList(ListAPIView):
    model = Category


class GenreList(ListAPIView):
    model = Genre


class ContentDetail(DetailAPIView):
    model = Content


class CategoryDetail(DetailAPIView):
    model = Category


class GenreDetail(DetailAPIView):
    model = Genre


class TranslationDetail(DetailAPIView):
    model = Translation


class LineList(ListAPIView):
    model = Line

    def get_query(self, request, content_id: int):
        return Line.query.where(Line.content_id == content_id)

    @expect_query(page=(int, 1), content_id=(int, ...))
    async def get(self, request, page, content_id):
        return await super().get(request, page=page, content_id=content_id)

    async def post(self, request):
        raise ServerError("Not Allowed Method", 405)


class RandomSubtitles(APIView):
    """
    This view is temporarily serving for main page. 
    It will be replaced by a recommendation system or contents.
    """

    def _get_required_ids(self, lines: List[Dict[str, Any]]) -> Tuple[List[int]]:
        content_ids = []
        line_ids = []
        for each in lines:
            content_ids.append(each["content_id"])
            line_ids.append(each["id"])
        return content_ids, line_ids

    @jwt_optional
    @expect_query(count=(int, 30))
    async def get(self, requeest: Request, count: int, token: Optional[Token]):
        """
        Queries:
            count: approximated count to pick.
                It does not ensure **exact count**.
        """
        lines = await randomly_pick_subtitles(count)
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
        resp = data
        return JsonResponse(resp, status=200)


class SearchEnglish(APIView):
    def _get_required_ids(self, lines: List[Dict[str, Any]]) -> Tuple[List[int]]:
        content_ids = []
        line_ids = []
        for each in lines:
            content_ids.append(each["content_id"])
            line_ids.append(each["id"])
        return content_ids, line_ids

    @jwt_optional
    @expect_query(
        page=(int, 1), per_page=(int, 10), keyword=(constr(min_length=2), ...)
    )
    async def get(
        self, request, page: int, per_page: int, keyword: str, token: Optional[Token]
    ):
        """search english"""
        max_page, count = await calc_max_page(per_page, Line.line.op("~*")(keyword))
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "count": 0, "page": 0, "lines": [], "user_liked": []},
                status=200,
            )
        offset = per_page * (page - 1)
        lines = await search_english_lines(keyword, per_page, offset)
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
        return JsonResponse(resp, status=200)


class SearchKorean(APIView):
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
        page=(int, 1), per_page=(int, 10), keyword=(constr(min_length=2), ...)
    )
    async def get(
        self, request, page: int, per_page: int, keyword: str, token: Optional[Token]
    ):
        """search korean(translations)"""
        max_page, count = await calc_max_page(
            per_page, condition=Translation.translation.op("~*")(keyword)
        )
        offset = per_page * (page - 1)
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "page": 0, "count": 0, "lines": []}, status=200,
            )

        translations = await search_korean_lines(keyword, per_page, offset)
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
                "translation_count": translation_count.get(each["id"], 0),
                "genres": genres[each["content_id"]],
                "user_liked": each["id"] in user_liked,
            }
            for each in translations
        ]
        resp = {
            "max_page": max_page,
            "page": page,
            "count": count,
            "data": data,
        }
        return JsonResponse(resp)


class TranslationListView(APIView):
    @jwt_optional
    @expect_query(page=(int, 1), per_page=(int, 10), line_id=(int, ...))
    async def get(
        self,
        request: Request,
        page: int,
        per_page: int,
        line_id: int,
        token: Optional[Token],
    ):
        max_page, count = await calc_max_page(per_page, Translation.line_id == line_id)
        offset = per_page * (page - 1)
        if page > max_page:
            return JsonResponse(
                {"max_page": 0, "page": 0, "count": 0, "data": []}, status=200
            )

        translations = await get_translations(line_id, per_page, offset)
        translation_ids = [each["id"] for each in translations]
        like_count = await get_like_count_per_korean_line(translation_ids)
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
                "user_liked": each["id"] in user_liked,
            }
            for each in translations
        ]
        resp = {
            "max_page": max_page,
            "page": page,
            "count": count,
            "data": data,
        }
        return JsonResponse(resp)

    @jwt_required
    @expect_body(line_id=(int, ...), translation=(str, ...))
    async def post(self, request: Request, token: Token):
        user_id = token.identity
        translation = await Translation(**request.json, user_id=user_id).create()
        nickname = await User.select("nickname").where(User.id == user_id).gino.scalar()
        return JsonResponse(
            {**translation.to_dict(), "user": {"id": user_id, "nickname": nickname}},
            status=201,
        )


class TranslationDetailView(APIView, UpdateModelMixin, DestroyModelMixin):
    async def get_object(self, translation_id):
        return await get_translation(translation_id)

    @jwt_required
    async def put(self, request: Request, translation_id: int, token: Token):
        translation = await get_translation(translation_id)
        user_id = token.identity
        if user_id == translation.translatior_id:
            resp = await self.update(request, translation_id)
            return resp
        else:
            raise ServerError("permission denied", 403)

    @jwt_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        translation = await get_translation(translation_id)
        user_id = token.identity
        if user_id == translation.translatior_id:
            resp = await self.destroy(request, translation_id)
            return resp
        else:
            raise ServerError("permission denied", 403)


class LikeEnglish(APIView):
    @jwt_required
    async def post(self, request: Request, line_id: int, token: Token):
        user_id = token.identity
        try:
            await create_english_like(line_id, user_id)
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "already liked"}, status=400)
        return JsonResponse({"message": "liked"}, status=201)

    @jwt_required
    async def delete(self, request: Request, line_id: int, token: Token):
        user_id = token.identity
        await delete_english_like(line_id, user_id)
        return JsonResponse({"message": "deleted like"}, status=204)


class LikeKorean(APIView):
    @jwt_required
    async def post(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        try:
            await create_korean_like(translation_id, user_id)
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "already liked"}, status=400)
        return JsonResponse({"message": "liked"}, status=201)

    @jwt_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        await delete_korean_like(translation_id, user_id)
        return JsonResponse({"message": "deleted like"}, status=204)


blueprint.add_route(ContentList.as_view(), "/contents")
blueprint.add_route(CategoryList.as_view(), "/categories")
blueprint.add_route(GenreList.as_view(), "/genres")
blueprint.add_route(ContentDetail.as_view(), "/contents/<id:int>"),
blueprint.add_route(LineList.as_view(), "/contents/<content_id:int>/lines"),
blueprint.add_route(CategoryDetail.as_view(), "/categories/<id:int>")
blueprint.add_route(GenreDetail.as_view(), "/genres/<id:int>")
blueprint.add_route(RandomSubtitles.as_view(), "/random/subtitles")
blueprint.add_route(SearchEnglish.as_view(), "/search/english")
blueprint.add_route(SearchKorean.as_view(), "/search/korean")
blueprint.add_route(TranslationDetail.as_view(), "/translations/<id:int>")
blueprint.add_route(TranslationListView.as_view(), "/translations")
blueprint.add_route(
    TranslationDetailView.as_view(), "/translations/<translation_id:int>"
)
blueprint.add_route(LikeEnglish.as_view(), "/likes/english/<line_id:int>")
blueprint.add_route(LikeKorean.as_view(), "/likes/korean/<translation_id:int>")
