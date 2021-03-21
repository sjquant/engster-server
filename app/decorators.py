from typing import Dict, Tuple, Any
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


def _parse_query(
    query_args: Tuple[str, Any], field_definitions: Dict[str, Any]
) -> Dict[str, Any]:

    new_args = {}
    for key, val in query_args:
        field_val = field_definitions[key]
        if isinstance(field_val, tuple):
            type_hint = field_val[0]
        else:
            type_hint = field_val

        try:
            origin = type_hint.__origin__()
        except AttributeError:
            origin = type_hint

        if isinstance(origin, list):
            try:
                new_args[key].append(val)
            except KeyError:
                new_args[key] = [val]
        else:
            new_args[key] = val
    return new_args


def expect_query(**field_definitions):
    def actual_expect_query(func):
        model = create_model(f"QUERY_{uuid.uuid4().hex}", **field_definitions)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = _get_request(*args)
            parsed_query_args = _parse_query(request.query_args, field_definitions)
            processed = model(**parsed_query_args).dict()
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
