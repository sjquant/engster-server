from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint
from sanic_jwt_extended.tokens import Token

from app.models import Genre
from app.decorators import expect_body, admin_required
from app.services import genre as service
from app.utils import JsonResponse

blueprint = Blueprint("genre_blueprint", url_prefix="/genres")


class GenreList(HTTPMethodView):
    async def get(self, request: Request):
        genres = await service.fetch_all()
        return JsonResponse({"data": genres}, 200)

    @expect_body(genre=(str, ...))
    @admin_required
    async def post(self, request: Request, token: Token):
        genre = await Genre(**request.json).create()
        return JsonResponse(genre.to_dict(), status=200)


class GenreDetail(HTTPMethodView):
    async def get(self, request, genre_id: int):
        genre = await service.get_by_id(genre_id)
        if not genre:
            raise ServerError("no such genre", 404)
        return JsonResponse(genre.to_dict(), 200)

    @admin_required
    async def put(self, request: Request, genre_id: int, token: Token):
        genre = await service.get_by_id(genre_id)
        if not genre:
            raise ServerError("no such genre", 404)
        await genre.update(**request.json).apply()
        return JsonResponse({"message": "success"}, status=202)

    @admin_required
    async def delete(self, request: Request, genre_id: int, token: Token):
        genre = await service.get_by_id(genre_id)
        if not genre:
            raise ServerError("no such genre", 404)
        await genre.delete()
        return JsonResponse({"message": "success"}, status=204)


blueprint.add_route(GenreList.as_view(), "")
blueprint.add_route(GenreDetail.as_view(), "/<genre_id:int>")
