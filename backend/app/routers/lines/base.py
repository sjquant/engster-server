from app import models
from app.utils.baserouter import ListRouter, DetailRouter
from .blueprint import lines_bp


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

    def get_query(self, content_id):
        return models.Line.query.where(models.Line.content_id == content_id)


class CategoryDetail(DetailRouter):
    model = models.Category
    list_display = ['id', 'category']


class GenreDetail(DetailRouter):
    model = models.Genre
    list_display = ['id', 'genre']


lines_bp.add_route(ContentList.as_view(), '/contents')
lines_bp.add_route(CategoryList.as_view(), '/categories')
lines_bp.add_route(GenreList.as_view(), '/genres')
lines_bp.add_route(LineList.as_view(), '/lines/<content_id:int>')
lines_bp.add_route(CategoryDetail.as_view(), '/categories/<id:int>')
lines_bp.add_route(GenreDetail.as_view(), '/genres/<id:int>')
