from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint

from app import models
from app.utils.router import ListRouter, DetailRouter

blueprint = Blueprint('base_blueprint', url_prefix='')


class ContentList(ListRouter):
    model = models.Content
    list_display = ['id', 'title', 'year']


class CategoryList(ListRouter):
    model = models.Category
    list_display = ['id', 'category']


class GenreList(ListRouter):
    model = models.Genre
    list_display = ['id', 'genre']


class LineList(ListRouter):
    model = models.Line
    list_display = ['id', 'time', 'line']

    def get_query(self, request):
        content_id = request.args.get('content_id')
        if not content_id:
            ServerError("content_id is required", 422)
        return models.Line.query.where(
            models.Line.content_id == int(content_id))

    def post(self, request):
        raise ServerError("Not Allowed Method", 405)


class CategoryDetail(DetailRouter):
    model = models.Category
    list_display = ['id', 'category']


class GenreDetail(DetailRouter):
    model = models.Genre
    list_display = ['id', 'genre']


class TranslationDetail(DetailRouter):

    model = models.Translation


blueprint.add_route(ContentList.as_view(), '/contents')
blueprint.add_route(CategoryList.as_view(), '/categories')
blueprint.add_route(GenreList.as_view(), '/genres')
blueprint.add_route(LineList.as_view(), '/lines')
blueprint.add_route(CategoryDetail.as_view(), '/categories/<id:int>')
blueprint.add_route(GenreDetail.as_view(), '/genres/<id:int>')
blueprint.add_route(TranslationDetail.as_view(), '/translations/<id:int>')
