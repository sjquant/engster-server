from functools import wraps
import asyncio
import uuid

from sanic.request import Request
from pydantic import create_model, BaseModel


def _get_request(*args):
    """
    Get request object from args.
    """
    if isinstance(args[0], Request):
        request = args[0]
    else:
        request = args[1]
    return request


def expect_query(**field_definitions):
    def actual_expect_query(func):
        model = create_model(f"QUERY_{uuid.uuid4().hex}", **field_definitions)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = _get_request(*args)
            processed = model(**dict(request.query_args)).dict()
            kwargs.update(processed)
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return actual_expect_query


def expect_body(**field_definitions):
    def actual_expect_body(func):
        model = create_model(f"BODY_{uuid.uuid4().hex}", **field_definitions)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = _get_request(*args)
            processed = model(**request.json).dict()
            # update parsed_json (which is called by request.json)
            request.parsed_json = processed
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return actual_expect_body


def expect_query_with_model(model: BaseModel):
    def actual_expect_query(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = _get_request(*args)
            processed = model(**dict(request.query_args)).dict()
            kwargs.update(processed)
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return actual_expect_query


def expect_body_with_model(model: BaseModel):
    def actual_expect_body(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = _get_request(*args)
            processed = model(**request.json).dict()
            # update parsed_json (which is called by request.json)
            request.parsed_json = processed
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return actual_expect_body
