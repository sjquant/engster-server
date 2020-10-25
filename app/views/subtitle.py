from typing import List, Tuple, Dict, Any, Optional

import asyncpg
from pydantic import constr
from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint
from sanic_jwt_extended import jwt_required, jwt_optional
from sanic_jwt_extended.tokens import Token

from app.db_models import (
    User,
    Translation,
    Genre,
    Content,
)
from app.decorators import expect_query, expect_body, admin_required
from app.services import subtitle as service
from app.utils import JsonResponse
from app import db

blueprint = Blueprint("subtitle_blueprint", url_prefix="subtitle")


class ContentList(HTTPMethodView):
    @expect_query(limit=(int, 10), cursor=(int, None))
    async def get(self, request: Request, limit: int, cursor: int):
        contents = await service.fetch_contents(limit, cursor)
        genres = await service.fetch_genres_per_content(
            [each["id"] for each in contents]
        )
        data = [{**each, "genres": genres.get(each["id"], [])} for each in contents]
        return JsonResponse({"data": data}, 200)

    @expect_body(title=(str, ...), year=(str, ...), poster=(str, ""))
    @admin_required
    async def post(self, request: Request, token: Token):
        """
        Create content
        """
        content = await Content(**request.json).create()
        return JsonResponse(content.to_dict(), status=201)


class ContentXGenreList(HTTPMethodView):
    async def get(self, request: Request, content_id: int):
        """
        Fetch genres to content
        """
        res = await service.fetch_genres_per_content([content_id])
        genres = res.get(content_id, [])
        return JsonResponse(genres, status=200)

    @expect_body(genre_ids=(List[int], ...))
    @admin_required
    async def post(self, request: Request, content_id: int, token: Token):
        """
        Add genres to content
        """
        content = await service.get_content_by_id(content_id)
        genre_ids = request.json["genre_ids"]
        if not content:
            raise ServerError("no such content", 404)

        genres = await service.fetch_genres_by_ids(genre_ids)
        if len(genre_ids) != len(genres):
            raise ServerError("some genres are missing", 400)

        await service.add_genres_to_content(content, genres)
        return JsonResponse({"message": "success"}, status=201)

    @expect_body(genre_ids=(List[int], ...))
    @admin_required
    async def put(self, request: Request, content_id: int, token: Token):
        """
        Update genres of contents
        """
        content = await service.get_content_by_id(content_id)
        genre_ids = request.json["genre_ids"]
        if not content:
            raise ServerError("no such content", 404)

        genres = await service.fetch_genres_by_ids(genre_ids)
        if len(genre_ids) != len(genres):
            raise ServerError("some genres are missing", 400)

        async with db.transaction():
            await service.empty_content_of_gneres(content_id)
            await service.add_genres_to_content(content, genres)
        return JsonResponse({"message": "success"}, status=202)


class GenreList(HTTPMethodView):
    async def get(self, request: Request):
        genres = await service.fetch_all_genres()
        return JsonResponse({"data": genres}, 200)

    @expect_body(genre=(str, ...))
    @admin_required
    async def post(self, request: Request, token: Token):
        genre = await Genre(**request.json).create()
        return JsonResponse(genre.to_dict(), status=200)


class LineList(HTTPMethodView):
    @expect_query(cursor=(int, None), limit=(int, 20))
    async def get(self, request: Request, content_id: int, cursor: int, limit: int):
        lines = await service.fetch_content_lines(content_id, limit, cursor)
        return JsonResponse(lines, status=200)


class ContentDetail(HTTPMethodView):
    async def get(self, request: Request, content_id: int):
        content = await service.get_content_by_id(content_id)
        if not content:
            raise ServerError("no such content", 404)
        genres = await service.fetch_genres_per_content([content_id])
        return JsonResponse(
            {**content.to_dict(), "genres": genres.get(content_id, [])}, 200
        )

    @admin_required
    async def put(self, request: Request, content_id: int, token: Token):
        content = await service.get_content_by_id(content_id)
        if not content:
            raise ServerError("no such content", 404)
        await content.update(**request.json).apply()
        return JsonResponse({"message": "success"}, status=202)

    @admin_required
    async def delete(self, request: Request, content_id: int, token: Token):
        content = await service.get_content_by_id(content_id)
        if not content:
            raise ServerError("no such content", 404)
        await content.delete()
        return JsonResponse({"message": "success"}, status=204)


class GenreDetail(HTTPMethodView):
    async def get(self, request, genre_id: int):
        genre = await service.get_genre_by_id(genre_id)
        if not genre:
            raise ServerError("no such genre", 404)
        return JsonResponse(genre.to_dict(), 200)

    @admin_required
    async def put(self, request: Request, genre_id: int, token: Token):
        genre = await service.get_genre_by_id(genre_id)
        if not genre:
            raise ServerError("no such genre", 404)
        await genre.update(**request.json).apply()
        return JsonResponse({"message": "success"}, status=202)

    @admin_required
    async def delete(self, request: Request, genre_id: int, token: Token):
        genre = await service.get_genre_by_id(genre_id)
        if not genre:
            raise ServerError("no such genre", 404)
        await genre.delete()
        return JsonResponse({"message": "success"}, status=204)


class RandomSubtitles(HTTPMethodView):
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
        lines = await service.randomly_pick_subtitles(count)
        content_ids, line_ids = self._get_required_ids(lines)
        like_count = await service.get_like_count_per_english_line(line_ids)
        translation_count = await service.get_translation_count_per_line(line_ids)
        genres = await service.fetch_genres_per_content(content_ids)
        user_id = token.identity if token else None
        user_liked = (
            await service.fetch_user_liked_english_lines(user_id, line_ids)
            if user_id
            else []
        )
        data = [
            {
                **line,
                "genres": genres.get(line["content_id"], []),
                "like_count": like_count.get(line["id"], 0),
                "translation_count": translation_count.get(line["id"], 0),
                "user_liked": line["id"] in user_liked,
            }
            for line in lines
        ]
        resp = {
            "max_page": 1,
            "page": 1,
            "count": len(data),
            "data": data,
        }
        return JsonResponse(resp, status=200)


class SearchEnglish(HTTPMethodView):
    def _get_required_ids(self, lines: List[Dict[str, Any]]) -> Tuple[List[int]]:
        content_ids = []
        line_ids = []
        for each in lines:
            content_ids.append(each["content_id"])
            line_ids.append(each["id"])
        return content_ids, line_ids

    @jwt_optional
    @expect_query(
        limit=(int, 20), cursor=(int, None), keyword=(constr(min_length=2), ...)
    )
    async def get(
        self, request, limit: int, cursor: int, keyword: str, token: Optional[Token]
    ):
        """search english"""

        count = await service.count_english_lines(keyword) if cursor is None else None
        if count == 0:
            return JsonResponse({"data": [], "count": 0, "cursor": cursor})

        lines = await service.search_english_lines(keyword, limit, cursor)
        content_ids, line_ids = self._get_required_ids(lines)
        like_count = await service.get_like_count_per_english_line(line_ids)
        translation_count = await service.get_translation_count_per_line(line_ids)
        genres = await service.fetch_genres_per_content(content_ids)
        user_id = token.identity if token else None
        user_liked = (
            await service.fetch_user_liked_english_lines(user_id, line_ids)
            if user_id
            else []
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
            "cursor": cursor,
            "count": count,
            "data": data,
        }
        return JsonResponse(resp, status=200)


class SearchKorean(HTTPMethodView):
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
        count = await service.count_korean_lines(keyword) if cursor is None else None
        if count == 0:
            return JsonResponse({"data": [], "count": 0, "cursor": cursor})

        translations = await service.search_korean_lines(keyword, limit, cursor)
        content_ids, translation_ids, line_ids = self._get_required_ids(translations)
        genres = await service.fetch_genres_per_content(content_ids)
        like_count = await service.get_like_count_per_korean_line(translation_ids)
        translation_count = await service.get_translation_count_per_line(line_ids)
        user_id = token.identity if token else None
        user_liked = (
            await service.fetch_user_liked_korean_lines(user_id, translation_ids)
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
            "cursor": cursor,
            "count": count,
            "data": data,
        }
        return JsonResponse(resp)


class TranslationList(HTTPMethodView):
    @jwt_optional
    @expect_query(limit=(int, 20), cursor=(int, None), line_id=(int, ...))
    async def get(
        self,
        request: Request,
        limit: int,
        cursor: int,
        line_id: int,
        token: Optional[Token],
    ):
        translations = await service.fetch_translations(line_id, limit, cursor)
        translation_ids = [each["id"] for each in translations]
        like_count = await service.get_like_count_per_korean_line(translation_ids)
        user_id = token.identity if token else None
        user_liked = (
            await service.fetch_user_liked_korean_lines(user_id, translation_ids)
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
        resp = {"cursor": cursor, "data": data}
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


class TranslationDetail(HTTPMethodView):
    async def get(self, request, translation_id: int):
        translation = await service.get_translation_by_id(translation_id)
        if not translation:
            raise ServerError("no such translation", 404)
        return JsonResponse(translation.to_dict(), 200)

    @jwt_required
    async def put(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        translation = await service.get_translation_by_id(translation_id)
        if not translation:
            raise ServerError("no such translation", 404)

        if user_id == translation.translatior_id:
            await translation.update(**request.json).apply()
            return JsonResponse({"message": "success"}, 202)
        else:
            raise ServerError("permission denied", 403)

    @jwt_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        translation = await service.get_translation_by_id(translation_id)
        if not translation:
            raise ServerError("no such translation", 404)

        if user_id == translation.translatior_id:
            await translation.delete()
            resp = await translation.destroy(request, translation_id)
            return resp
        else:
            raise ServerError("permission denied", 403)


class LikeEnglish(HTTPMethodView):
    @jwt_required
    async def post(self, request: Request, line_id: int, token: Token):
        user_id = token.identity
        try:
            await service.create_english_like(line_id, user_id)
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "already liked"}, status=400)
        return JsonResponse({"message": "liked"}, status=201)

    @jwt_required
    async def delete(self, request: Request, line_id: int, token: Token):
        user_id = token.identity
        await service.delete_english_like(line_id, user_id)
        return JsonResponse({"message": "deleted like"}, status=204)


class LikeKorean(HTTPMethodView):
    @jwt_required
    async def post(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        try:
            await service.create_korean_like(translation_id, user_id)
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "already liked"}, status=400)
        return JsonResponse({"message": "liked"}, status=201)

    @jwt_required
    async def delete(self, request: Request, translation_id: int, token: Token):
        user_id = token.identity
        await service.delete_korean_like(translation_id, user_id)
        return JsonResponse({"message": "deleted like"}, status=204)


blueprint.add_route(ContentList.as_view(), "/contents")
blueprint.add_route(GenreList.as_view(), "/genres")
blueprint.add_route(ContentXGenreList.as_view(), "/contents/<content_id:int>/genres")
blueprint.add_route(ContentDetail.as_view(), "/contents/<content_id:int>"),
blueprint.add_route(LineList.as_view(), "/contents/<content_id:int>/lines")
blueprint.add_route(GenreDetail.as_view(), "/genres/<genre_id:int>")
blueprint.add_route(RandomSubtitles.as_view(), "/random/subtitles")
blueprint.add_route(SearchEnglish.as_view(), "/search/english")
blueprint.add_route(SearchKorean.as_view(), "/search/korean")
blueprint.add_route(TranslationList.as_view(), "/translations")
blueprint.add_route(TranslationDetail.as_view(), "/translations/<translation_id:int>")
blueprint.add_route(LikeEnglish.as_view(), "/likes/english/<line_id:int>")
blueprint.add_route(LikeKorean.as_view(), "/likes/korean/<translation_id:int>")
