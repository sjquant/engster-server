from typing import Tuple, Optional

from sanic.response import json
from sanic.exceptions import ServerError
from sanic.views import HTTPMethodView

from app import db
from app.utils.serializer import jsonify


class ListRouter(HTTPMethodView):

    model: Optional[db.Model] = None
    list_display: Optional[list] = None
    page_size: Optional[int] = None

    def get_query(self, request, *args, **kwargs):
        return self.model.query

    def get_pagesize_and_offset(self, request) -> Tuple[int, int]:
        # pagination
        app = request.app
        page = int(request.args.get('page', 1))
        page_size = self.page_size if self.page_size else app.config.get(
            'PAGE_SIZE', 20)
        offset = (page-1) * page_size
        return page_size, offset

    async def get(self, request, *args, **kwargs) -> json:

        query = self.get_query(request, *args, **kwargs)
        pagesize, offset = self.get_pagesize_and_offset(request)

        data = await query.limit(pagesize).offset(offset).gino.all()

        res = [
            each.to_dict(show=self.list_display)
            for each in data
        ]
        return jsonify(res, status=200)

    async def post(self, request):

        instance = self.model(**request.json)
        await instance.create()
        return jsonify(instance.to_dict(show=self.list_display), status=201)


class DetailRouter(HTTPMethodView):

    # Model
    model: Optional[db.Model] = None
    list_display: Optional[list] = None

    async def get_instance(self, id):
        instance = await self.model.get(id)
        if instance is None:
            raise ServerError('No Such Instance', status_code=404)
        return instance

    async def get(self, request, id):
        instance = await self.get_instance(id)
        return jsonify(instance.to_dict(show=self.list_display), status=200)

    async def put(self, request, id):
        instance = await self.get_instance(id)
        await instance.update(**request.json).apply()
        return jsonify(instance.to_dict(show=self.list_display), status=202)

    async def delete(self, request, id):
        instance = await self.get_instance(id)
        await instance.delete()
        return jsonify(None, status=204)
