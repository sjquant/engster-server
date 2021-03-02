# This core file is used to replace or supplement
# [SANIC-JWT-EXTENDED](https://github.com/NovemberOscar/Sanic-JWT-Extended) library

from functools import wraps, partial
from typing import Optional
import datetime
import uuid
import jwt

from sanic_jwt_extended.jwt_manager import JWT
from sanic_jwt_extended.decorators import (
    _get_request,
    _get_raw_jwt_from_request,
    _csrf_check,
    jwt_required,
)
from sanic_jwt_extended.exceptions import WrongTokenError, AccessDeniedError
from sanic_jwt_extended.tokens import Token


def get_csrf_token(encoded_token):
    token = Token(encoded_token)
    return token.csrf


# override Sanic-JWT-Extended's _encode_jwt for csrf
def encode_jwt(cls, token_type, payload, expires_delta):
    algorithm = cls.config.algorithm
    secret = (
        cls.config.secret_key if algorithm.startswith("HS") else cls.config.private_key
    )

    iss = payload.pop("iss") if payload.get("iss") else cls.config.default_iss
    aud = payload.pop("aud") if payload.get("aud") else cls.config.default_aud
    iat = datetime.datetime.utcnow()
    nbf = payload.pop("nbf") if payload.get("nbf") else iat
    jti = uuid.uuid4().hex

    reserved_claims = {"iss": iss, "aud": aud, "jti": jti, "iat": iat, "nbf": nbf}

    if isinstance(expires_delta, datetime.timedelta):
        reserved_claims["exp"] = iat + expires_delta

    if "cookies" in cls.config.token_location and cls.config.csrf_protect:
        reserved_claims["csrf"] = uuid.uuid4().hex

    payload.update(reserved_claims)
    payload = {k: v for k, v in payload.items() if v is not None}

    header = {"class": token_type}

    token = jwt.encode(
        payload, secret, algorithm, header, cls.config.json_encoder
    ).decode("utf-8")

    return token


def set_jwt_cookie(response, encoded_token, *, max_age=None, is_access=True):
    """
    Set the access JWT in the cookie
    """
    cookie_key = JWT.config.jwt_cookie if is_access else JWT.config.refresh_jwt_cookie
    response.cookies[cookie_key] = encoded_token
    cookie = response.cookies[cookie_key]
    cookie["max-age"] = max_age or 31540000  # 1 year
    cookie["httponly"] = True
    cookie["samesite"] = "lax"
    cookie["secure"] = JWT.config.cookie_secure
    cookie["path"] = "/"
    if JWT.config.cookie_domain:
        cookie["domain"] = JWT.config.cookie_domain

    if JWT.config.csrf_protect:
        cookie_csrf_key = (
            JWT.config.jwt_csrf_header
            if is_access
            else JWT.config.refresh_jwt_csrf_header
        )
        response.cookies[cookie_csrf_key] = get_csrf_token(encoded_token)
        csrf_cookie = response.cookies[cookie_csrf_key]
        csrf_cookie["max-age"] = max_age or 31540000
        csrf_cookie["httponly"] = False
        csrf_cookie["samesite"] = "lax"
        csrf_cookie["secure"] = JWT.config.cookie_secure
        csrf_cookie["path"] = "/"
        if JWT.config.cookie_domain:
            csrf_cookie["domain"] = JWT.config.cookie_domain


set_access_cookie = partial(set_jwt_cookie, is_access=True)
set_refresh_cookie = partial(set_jwt_cookie, is_access=False)


def remove_jwt_cookie(response, is_access=True):
    """Remove jwt cookies"""
    cookie_key = JWT.config.jwt_cookie if is_access else JWT.config.refresh_jwt_cookie
    response.cookies[cookie_key] = ""

    cookie = response.cookies[cookie_key]
    cookie["max-age"] = -9999
    cookie["httponly"] = True
    cookie["samesite"] = "lax"
    cookie["secure"] = JWT.config.cookie_secure
    cookie["path"] = "/"

    if JWT.config.cookie_domain:
        cookie["domain"] = JWT.config.cookie_domain

    if JWT.config.csrf_protect:
        cookie_csrf_key = (
            JWT.config.jwt_csrf_header
            if is_access
            else JWT.config.refresh_jwt_csrf_header
        )
        response.cookies[cookie_csrf_key] = ""
        csrf_cookie = response.cookies[cookie_csrf_key]
        csrf_cookie["max-age"] = -9999
        csrf_cookie["httponly"] = False
        csrf_cookie["samesite"] = "lax"
        csrf_cookie["secure"] = JWT.config.cookie_secure
        csrf_cookie["path"] = "/"
        if JWT.config.cookie_domain:
            csrf_cookie["domain"] = JWT.config.cookie_domain


remove_access_cookie = partial(remove_jwt_cookie, is_access=True)
remove_refresh_cookie = partial(remove_jwt_cookie, is_access=False)


def jwt_optional(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        request = _get_request(args)
        token_obj: Optional[Token] = None

        try:
            raw_jwt, csrf_value = _get_raw_jwt_from_request(request)
            token_obj = Token(raw_jwt)

            if csrf_value:
                _csrf_check(csrf_value, token_obj.csrf)

            if token_obj.type != "access":
                raise WrongTokenError("Only access tokens are allowed")

        except Exception:
            pass

        kwargs["token"] = token_obj

        return await function(*args, **kwargs)

    return wrapper


def admin_required(func):
    @jwt_required(allow=["admin"])
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def self_required(func):
    @jwt_required
    def wrapper(*args, **kwargs):
        token = kwargs["token"]
        user_id = kwargs["user_id"]
        if token.identity != str(user_id):
            raise AccessDeniedError("Permission Denied")
        return func(*args, **kwargs)

    return wrapper
