from typing import List, Optional

from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic.blueprints import Blueprint
from sanic_jwt_extended.tokens import Token

from app.models import Content
from app.decorators import expect_query, expect_body
from app.core.sanic_jwt_extended import admin_required
from app.services import content as service
from app.utils import JsonResponse
from app import db

blueprint = Blueprint("content_blueprint", url_prefix="/contents")


class ContentList(HTTPMethodView):
    @expect_query(limit=(int, 10), cursor=(int, None))
    async def get(self, request: Request, limit: int, cursor: Optional[int]):
        contents = await service.fetch(limit, cursor)
        genres = await service.fetch_genres([each["id"] for each in contents])
        data = [{**each, "genres": genres.get(each["id"], [])} for each in contents]
        return JsonResponse({"data": data}, 200)

    @expect_body(
        title=(str, ...), year=(str, ...), poster=(str, ""), genre_ids=(List[int], [])
    )
    @admin_required
    async def post(self, request: Request, token: Token):
        """
        Create content
        """
        data = request.json
        async with db.transaction():
            content = await Content(
                title=data["title"], year=data["year"], poster=data["poster"]
            ).create()
            await service.add_genres(content, data["genre_ids"])
        return JsonResponse({"message": "success"}, status=201)


class ContentDetail(HTTPMethodView):
    async def get(self, request: Request, content_id: int):
        content = await service.get_by_id(content_id)
        if not content:
            return JsonResponse({"message": "Content not found"}, status=404)
        genres = await service.fetch_genres([content_id])
        return JsonResponse(
            {**content.to_dict(), "genres": genres.get(content_id, [])}, 200
        )

    @expect_body(
        title=(str, ...), year=(str, ...), poster=(str, ""), genre_ids=(List[int], ...)
    )
    @admin_required
    async def put(self, request: Request, content_id: int, token: Token):
        data = request.json
        content = await service.get_by_id(content_id)
        if not content:
            return JsonResponse({"message": "Content not found"}, status=404)

        async with db.transaction():
            await content.update(
                title=data["title"], poster=data["poster"], year=data["year"]
            ).apply()
            await service.clear_genres(content_id)
            await service.add_genres(content, data["genre_ids"])
        return JsonResponse({"message": "success"}, status=200)

    @admin_required
    async def delete(self, request: Request, content_id: int, token: Token):
        content = await service.get_by_id(content_id)
        if not content:
            return JsonResponse({"message": "Content not found"}, status=404)
        await content.delete()
        return JsonResponse({"message": "success"}, status=204)


blueprint.add_route(ContentList.as_view(), "")
blueprint.add_route(ContentDetail.as_view(), "/<content_id:int>"),
