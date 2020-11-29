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

from app.models import User, Subtitle, Translation, Content
from app.decorators import expect_query, expect_body, admin_required
from app.services import subtitle as subtitle_service
from app.services import content as content_service
from app.services import translation as translation_service
from app import db
from app.utils import JsonResponse

blueprint = Blueprint("subtitle_blueprint", url_prefix="/subtitles")


class SubtitleList(HTTPMethodView):
    @expect_query(content_id=(int, None), cursor=(int, None), limit=(int, 20))
    async def get(self, request: Request, content_id: int, cursor: int, limit: int):

        data = []

        if content_id:
            data = await subtitle_service.fetch_by_content_id(content_id, limit, cursor)

        resp = {
            "cursor": cursor,
            "data": data,
        }
        return JsonResponse(resp, status=200)

    async def _upload_subtitle(self, df):
        subtitle = df[["time", "line", "content_id"]]
        subtitltes = subtitle.to_dict(orient="records")
        return await Subtitle.insert().gino.all(subtitltes)

    @admin_required
    @expect_query(content_id=(int, ...))
    async def post(self, request: Request, content_id: int, token: Token):
        content = await Content.get(content_id)
        if content is None:
            raise ServerError("No Such Instance", status_code=404)

        input_file = request.files.get("input")
        data = BytesIO(input_file.body)
        df = pd.read_csv(data, encoding="utf-8")
        df["content_id"] = content_id
        async with db.transaction():
            data = await self._upload_subtitle(df)
            print(data)
        # await self._upload_translation(df)

        return JsonResponse({"message": "Hi"})


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
    @expect_query(max_count=(int, 30))
    async def get(self, requeest: Request, max_count: int, token: Optional[Token]):
        """
        Queries:
            max_count: Maximum count to pick
                It does not ensure **exact count**.
        """
        lines = await subtitle_service.pick_randomly(max_count)
        content_ids, line_ids = self._get_required_ids(lines)
        like_count = await subtitle_service.fetch_like_count(line_ids)
        translation_count = await subtitle_service.fetch_translation_count(line_ids)
        genres = await content_service.fetch_genres(content_ids)
        user_id = token.identity if token else None
        user_liked = (
            await subtitle_service.pick_user_liked(user_id, line_ids) if user_id else []
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


class SearchSubtitles(HTTPMethodView):
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

        count = await subtitle_service.count(keyword) if cursor is None else None
        if count == 0:
            return JsonResponse({"data": [], "count": 0, "cursor": cursor})

        lines = await subtitle_service.search(keyword, limit, cursor)
        content_ids, line_ids = self._get_required_ids(lines)
        like_count = await subtitle_service.fetch_like_count(line_ids)
        translation_count = await subtitle_service.fetch_translation_count(line_ids)
        genres = await content_service.fetch_genres(content_ids)
        user_id = token.identity if token else None
        user_liked = (
            await subtitle_service.pick_user_liked(user_id, line_ids) if user_id else []
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


class TranslationList(HTTPMethodView):
    @jwt_optional
    @expect_query(limit=(int, 20), cursor=(int, None))
    async def get(
        self,
        request: Request,
        line_id: int,
        limit: int,
        cursor: int,
        token: Optional[Token],
    ):
        translations = await subtitle_service.fetch_translations(line_id, limit, cursor)
        translation_ids = [each["id"] for each in translations]
        like_count = await translation_service.get_like_count(translation_ids)
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
                "user_liked": each["id"] in user_liked,
            }
            for each in translations
        ]
        resp = {"cursor": cursor, "data": data}
        return JsonResponse(resp)

    @jwt_required
    @expect_body(translation=(str, ...))
    async def post(self, request: Request, line_id: int, token: Token):
        user_id = token.identity
        translation = await Translation(
            **request.json, line_id=line_id, user_id=user_id
        ).create()
        nickname = await User.select("nickname").where(User.id == user_id).gino.scalar()
        return JsonResponse(
            {**translation.to_dict(), "user": {"id": user_id, "nickname": nickname}},
            status=201,
        )


class LikeSubtitle(HTTPMethodView):
    @jwt_required
    async def post(self, request: Request, line_id: int, token: Token):
        user_id = token.identity
        try:
            await subtitle_service.add_like(line_id, user_id)
        except asyncpg.exceptions.UniqueViolationError:
            return JsonResponse({"message": "already liked"}, status=400)
        return JsonResponse({"message": "liked"}, status=201)

    @jwt_required
    async def delete(self, request: Request, line_id: int, token: Token):
        user_id = token.identity
        await subtitle_service.remove_like(line_id, user_id)
        return JsonResponse({"message": "deleted like"}, status=204)


class UserLikedSubtitles(HTTPMethodView):
    def _get_required_ids(self, lines: List[Dict[str, Any]]) -> Tuple[List[int]]:
        content_ids = []
        line_ids = []
        for each in lines:
            content_ids.append(each["content_id"])
            line_ids.append(each["id"])
        return content_ids, line_ids

    @jwt_optional
    @expect_query(user_id=(str, ...), limit=(int, 20), cursor=(int, None))
    async def get(
        self, request: Request, user_id: str, limit: int, cursor: int, token: Token
    ):
        lines = await subtitle_service.fetch_user_liked(
            user_id, limit=limit, cursor=cursor
        )
        content_ids, line_ids = self._get_required_ids(lines)
        like_count = await subtitle_service.fetch_like_count(line_ids)
        translation_count = await subtitle_service.fetch_translation_count(line_ids)
        genres = await content_service.fetch_genres(content_ids)
        user_id = token.identity if token else None
        user_liked = (
            await subtitle_service.pick_user_liked(user_id, line_ids) if user_id else []
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
            "limit": limit,
            "cursor": cursor,
            "data": data,
        }

        return JsonResponse(resp, status=200,)


blueprint.add_route(SubtitleList.as_view(), "")
blueprint.add_route(SearchSubtitles.as_view(), "/search")
blueprint.add_route(RandomSubtitles.as_view(), "/random")
blueprint.add_route(TranslationList.as_view(), "/<line_id:int>/translations")
blueprint.add_route(LikeSubtitle.as_view(), "/<line_id:int>/like")
blueprint.add_route(UserLikedSubtitles.as_view(), "/liked")
