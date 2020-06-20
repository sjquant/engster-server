"""
I refered to django-rest-framework mixins
(https://github.com/encode/django-rest-framework/blob/master/rest_framework/mixins.py)
"""
from typing import Tuple


from app.utils import JsonResponse


class CreateModelMixin:
    """Create a model instance"""

    async def create(self, request, *args, **kwargs):
        instance = self.model(**request.json)
        await instance.create()
        return JsonResponse(instance.to_dict(), status=201)


class ListModelMixin:
    """List a query"""

    pagination: bool = True
    page_size: int = 10

    def get_paginated_query(self, query, page=1) -> Tuple[int, int]:

        if not self.pagination:
            return query
        offset = (page - 1) * self.page_size
        return query.limit(self.page_size).offset(offset)

    async def list(self, request, *args, **kwargs):

        page = kwargs.pop("page", 1)
        query = self.get_paginated_query(
            self.get_query(request, *args, **kwargs), page=page
        )
        data = await query.gino.all()
        return JsonResponse([each.to_dict() for each in data], status=200)


class RetrieveModelMixin:
    """Retrieve a model instance"""

    async def retrieve(self, request, *args, **kwargs):
        return_obj = kwargs.pop("return_obj", False)
        instance = await self.get_object(*args, **kwargs)
        if return_obj:
            return instance
        else:
            return JsonResponse(instance.to_dict(), status=200)


class UpdateModelMixin:
    """Update a model instance"""

    async def update(self, request, *args, **kwargs):
        return_obj = kwargs.pop("return_obj", False)
        instance = await self.get_object(*args, **kwargs)
        data = {key: value for key, value in request.json.items() if value is not None}
        await instance.update(**data).apply()
        if return_obj:
            return instance
        else:
            return JsonResponse(instance.to_dict(), status=202)


class DestroyModelMixin:
    """Destroy a model instance"""

    async def destroy(self, request, *args, **kwargs):
        return_obj = kwargs.pop("return_obj", False)
        instance = await self.get_object(*args, **kwargs)
        await instance.delete()
        if return_obj:
            return instance
        else:
            return JsonResponse(status=204)
