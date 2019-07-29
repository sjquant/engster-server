from functools import wraps
import asyncio
import uuid

from sanic.request import Request
from pydantic import create_model


def _get_request(*args):
    """
    Get request object from args.
    """
    if isinstance(args[0], Request):
        request = args[0]
    else:
        request = args[1]
    return request


def validate_queries(**field_definitions):
    def actual_validate_queries(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = _get_request(*args)
            model = create_model(f"QUERY_{uuid.uuid4().hex}", **field_definitions)
            validated_queries = model(**dict(request.query_args)).dict()
            kwargs.update(validated_queries)
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return actual_validate_queries


def validate_body():
    pass


def validate_form():
    pass


def validate_response():
    pass
