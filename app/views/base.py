from sanic.exceptions import ServerError
from sanic.blueprints import Blueprint

from app import models
from app.utils.router import ListRouter, DetailRouter
from app.utils.serializer import jsonify

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
            ServerError("need line_id but did not get it", 400)
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


class TranslationList(ListRouter):

    model = models.Translation
    page_size = 5

    def get_query(self, request):
        line_id = request.args.get('line_id')
        if not line_id:
            ServerError("need line_id but did not get it", 400)
        return models.Translation.query.where(
            models.Translation.line_id == int(line_id)
        ).order_by(models.Translation.created_at.desc())

    async def post(self, request):
        line_id = request.args.get('line_id')
        if not line_id:
            ServerError("need line_id but did not get it", 400)
        instance = self.model(**request.json, line_id=int(line_id))
        await instance.create()
        return jsonify(instance.to_dict(show=self.list_display), status=201)


class TranslationDetail(DetailRouter):

    model = models.Translation


blueprint.add_route(ContentList.as_view(), '/contents')
blueprint.add_route(CategoryList.as_view(), '/categories')
blueprint.add_route(GenreList.as_view(), '/genres')
blueprint.add_route(LineList.as_view(), '/lines')
blueprint.add_route(CategoryDetail.as_view(), '/categories/<id:int>')
blueprint.add_route(GenreDetail.as_view(), '/genres/<id:int>')
blueprint.add_route(TranslationList.as_view(), 'translations')
blueprint.add_route(TranslationDetail.as_view(), 'translations/<id:int>')
