from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint

from app.db_models import Content, Category, Genre, Line, Translation
from app.utils.views import ListAPIView, DetailAPIView
from app.utils.validators import validate_queries


blueprint = Blueprint("admin_lines_blueprint")


class ContentList(ListAPIView):
    model = Content


class CategoryList(ListAPIView):
    model = Category


class GenreList(ListAPIView):
    model = Genre


class LineList(ListAPIView):
    model = Line

    def get_query(self, request, content_id: int):
        return Line.query.where(Line.content_id == content_id)

    @validate_queries(page=(int, 1), content_id=(int, ...))
    async def get(self, request, page, content_id):
        return await super().get(request, page=page, content_id=content_id)

    async def post(self, request):
        raise ServerError("Not Allowed Method", 405)


class CategoryDetail(DetailAPIView):
    model = Category


class GenreDetail(DetailAPIView):
    model = Genre


class TranslationDetail(DetailAPIView):
    model = Translation


blueprint.add_route(ContentList.as_view(), "/contents")
blueprint.add_route(CategoryList.as_view(), "/categories")
blueprint.add_route(GenreList.as_view(), "/genres")
blueprint.add_route(LineList.as_view(), "/lines")
blueprint.add_route(CategoryDetail.as_view(), "/categories/<id:int>")
blueprint.add_route(GenreDetail.as_view(), "/genres/<id:int>")
blueprint.add_route(TranslationDetail.as_view(), "/translations/<id:int>")
