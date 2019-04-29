from functools import wraps

from sanic.request import Request
from sanic_jwt_extended.decorators import (
    verify_jwt_data_type,
    get_jwt_data_in_request_header
)
from sanic_jwt_extended.tokens import Token


def _get_request(*args):
    """
    Get request object from args.
    """
    if isinstance(args[0], Request):
        request = args[0]
    else:
        request = args[1]
    return request


def jwt_required(fn):
    """
    A decorator to protect a Sanic endpoint.
    If you decorate an endpoint with this, it will ensure that the requester
    has a valid access token before allowing the endpoint to be called.
    and if token check passed this will insert Token object to kwargs,
    This does not check the freshness of the access token.
    See also: :func:`~sanic_jwt_extended.fresh_jwt_required`
    """
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        request = _get_request(*args)
        app = request.app
        token = await get_jwt_data_in_request_header(app, request)
        await verify_jwt_data_type(token, "access")
        kwargs["token"] = Token(app, token)

        return await fn(*args, **kwargs)
    return wrapper
