from typing import Optional

from sanic.exceptions import ServerError
from sanic.views import HTTPMethodView

from app import db
from .view_mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)


class APIView(HTTPMethodView):

    model: Optional[db.Model] = None
    lookup_field = None

    def get_query(self, request, *args, **kwargs):

        query = self.model.query

        assert query is not None, (
            "'%s' should either include a `model` attribute, "
            "or override the `get_query()` method." % self.__class__.__name__
        )
        return query

    async def get_object(self, *args, **kwargs):

        lookup_field = self.lookup_field or "id"
        try:
            field = getattr(self.model, lookup_field)
        except AttributeError:
            raise AssertionError(
                "'%s' should either include a `lookup_field` attribute, "
                "or override the `get_object()` method." % self.__class__.__name__
            )

        obj = await self.model.query.where(field == kwargs[lookup_field]).gino.first()
        if obj is None:
            raise ServerError("no such object", status_code=404)
        return obj


class ListAPIView(APIView, ListModelMixin, CreateModelMixin):
    async def get(self, request, *args, **kwargs):
        resp = await self.list(request, *args, **kwargs)
        return resp

    async def post(self, request, *args, **kwargs):
        resp = await self.create(request, *args, **kwargs)
        return resp


class DetailAPIView(APIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    async def get(self, request, *args, **kwargs):
        resp = await self.retrieve(request, *args, **kwargs)
        return resp

    async def put(self, request, *args, **kwargs):
        resp = await self.update(request, *args, **kwargs)
        return resp

    async def delete(self, request, *args, **kwargs):
        resp = await self.destroy(request, *args, **kwargs)
        return resp
