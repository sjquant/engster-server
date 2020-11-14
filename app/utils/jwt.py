import datetime
import uuid
import jwt

from sanic_jwt_extended.jwt_manager import JWT
from sanic_jwt_extended.tokens import Token


def get_csrf_token(encoded_token):
    token = Token(encoded_token)
    print(token.__dict__)
    return token.csrf


# override JWT's encode jwt for csrf
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
        reserved_claims["csrf"] = jti

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
    access_cookie["path"] = "/"
    if JWT.config.cookie_domain:
        access_cookie["domain"] = JWT.config.cookie_domain

    if JWT.config.csrf_protect:
        access_cookie_csrf_key = JWT.config.jwt_csrf_header
        response.cookies[access_cookie_csrf_key] = get_csrf_token(encoded_access_token)
        access_csrf_cookie = response.cookies[access_cookie_csrf_key]
        access_csrf_cookie["max-age"] = max_age or 31540000
        access_csrf_cookie["httponly"] = False
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
        refresh_csrf_cookie["path"] = "/"
        if JWT.config.cookie_domain:
            refresh_csrf_cookie["domain"] = JWT.config.cookie_domain
