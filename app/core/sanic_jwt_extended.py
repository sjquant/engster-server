# This core file is used to replace or supplement
# [SANIC-JWT-EXTENDED](https://github.com/NovemberOscar/Sanic-JWT-Extended) library

from functools import wraps
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


def set_access_cookies(response, encoded_access_token, max_age=None):
    """
    Set the access JWT in the cookie
    """
    access_cookie_key = JWT.config.jwt_cookie
    response.cookies[access_cookie_key] = encoded_access_token
    access_cookie = response.cookies[access_cookie_key]
    access_cookie["max-age"] = max_age or 31540000  # 1 year
    access_cookie["httponly"] = True
    access_cookie["samesite"] = "lax"
    access_cookie["secure"] = JWT.config.cookie_secure
    access_cookie["path"] = "/"
    if JWT.config.cookie_domain:
        access_cookie["domain"] = JWT.config.cookie_domain

    if JWT.config.csrf_protect:
        access_cookie_csrf_key = JWT.config.jwt_csrf_header
        response.cookies[access_cookie_csrf_key] = get_csrf_token(encoded_access_token)
        access_csrf_cookie = response.cookies[access_cookie_csrf_key]
        access_csrf_cookie["max-age"] = max_age or 31540000
        access_csrf_cookie["httponly"] = False
        access_csrf_cookie["samesite"] = "lax"
        access_csrf_cookie["secure"] = JWT.config.cookie_secure
        access_csrf_cookie["path"] = "/"
        if JWT.config.cookie_domain:
            access_csrf_cookie["domain"] = JWT.config.cookie_domain


def set_refresh_cookies(response, encoded_refresh_token, max_age=None):
    """
    Set the refresh JWT in the cookie
    """
    refresh_cookie_key = JWT.config.refresh_jwt_cookie
    response.cookies[refresh_cookie_key] = encoded_refresh_token
    refresh_cookie = response.cookies[refresh_cookie_key]
    refresh_cookie["max-age"] = max_age or 31540000  # 1 year
    refresh_cookie["httponly"] = True
    refresh_cookie["samesite"] = "lax"
    refresh_cookie["secure"] = JWT.config.cookie_secure
    refresh_cookie["path"] = "/"
    if JWT.config.cookie_domain:
        refresh_cookie["domain"] = JWT.config.cookie_domain

    if JWT.config.csrf_protect:
        refresh_cookie_csrf_key = JWT.config.refresh_jwt_csrf_header
        response.cookies[refresh_cookie_csrf_key] = get_csrf_token(
            encoded_refresh_token
        )
        refresh_csrf_cookie = response.cookies[refresh_cookie_csrf_key]
        refresh_csrf_cookie["max-age"] = max_age or 31540000
        refresh_csrf_cookie["httponly"] = False
        refresh_csrf_cookie["samesite"] = "lax"
        refresh_csrf_cookie["secure"] = JWT.config.cookie_secure
        refresh_csrf_cookie["path"] = "/"
        if JWT.config.cookie_domain:
            refresh_csrf_cookie["domain"] = JWT.config.cookie_domain


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
