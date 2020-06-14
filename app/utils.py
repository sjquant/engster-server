from typing import Tuple, Any, List, Set, Optional
from enum import Enum
from types import GeneratorType
from uuid import UUID
import datetime
import math
import uuid
import jwt

from sqlalchemy.sql.elements import BinaryExpression
from pydantic import BaseModel
from pydantic.json import ENCODERS_BY_TYPE
from sanic.response import json
from sanic_jwt_extended.jwt_manager import JWT
from sanic_jwt_extended.tokens import Token

from app import db


Token.JWT = JWT


# jsonable_encoder is copy-and-paste version of fastapi
# (https://github.com/tiangolo/fastapi/tree/master/fastapi)


def jsonable_encoder(
    obj: Any,
    include: Set[str] = None,
    exclude: Set[str] = set(),
    by_alias: bool = True,
    skip_defaults: bool = False,
    include_none: bool = True,
    custom_encoder: dict = {},
    sqlalchemy_safe: bool = True,
) -> Any:
    if include is not None and not isinstance(include, set):
        include = set(include)
    if exclude is not None and not isinstance(exclude, set):
        exclude = set(exclude)
    if isinstance(obj, BaseModel):
        encoder = getattr(obj.Config, "json_encoders", custom_encoder)
        return jsonable_encoder(
            obj.dict(
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
            ),
            include_none=include_none,
            custom_encoder=encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (str, int, float, type(None))):
        return obj
    if isinstance(obj, dict):
        encoded_dict = {}
        for key, value in obj.items():
            if (
                (
                    not sqlalchemy_safe
                    or (not isinstance(key, str))
                    or (not key.startswith("_sa"))
                )
                and (value is not None or include_none)
                and ((include and key in include) or key not in exclude)
            ):
                encoded_key = jsonable_encoder(
                    key,
                    by_alias=by_alias,
                    skip_defaults=skip_defaults,
                    include_none=include_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_value = jsonable_encoder(
                    value,
                    by_alias=by_alias,
                    skip_defaults=skip_defaults,
                    include_none=include_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_dict[encoded_key] = encoded_value
        return encoded_dict
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        encoded_list = []
        for item in obj:
            encoded_list.append(
                jsonable_encoder(
                    item,
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    skip_defaults=skip_defaults,
                    include_none=include_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
            )
        return encoded_list
    errors: List[Exception] = []
    try:
        if custom_encoder and type(obj) in custom_encoder:
            encoder = custom_encoder[type(obj)]
        else:
            encoder = ENCODERS_BY_TYPE[type(obj)]
        return encoder(obj)
    except KeyError as e:
        errors.append(e)
        try:
            data = dict(obj)
        except Exception as e:
            errors.append(e)
            try:
                data = vars(obj)
            except Exception as e:
                errors.append(e)
                raise ValueError(errors)
    return jsonable_encoder(
        data,
        by_alias=by_alias,
        skip_defaults=skip_defaults,
        include_none=include_none,
        custom_encoder=custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )


def JsonResponse(
    obj: Any = None,
    status: int = 200,
    headers: Optional[dict] = None,
    content_type: str = "application/json",
    **kwargs
):
    return json(
        jsonable_encoder(obj, **kwargs),
        ensure_ascii=False,
        headers=headers,
        status=status,
        content_type=content_type,
    )


async def calc_max_page(page_size: int, condition: BinaryExpression) -> Tuple[int, int]:
    """
    Calculate Max Page

    Args:
        page_size: page size
        condition: gino conditional expression used in where

    Returns:
        max_page: maximum page
        count: total count
    """
    try:
        count = await db.select([db.func.count()]).where(condition).gino.scalar()
    except AttributeError:
        return 0, 0
    return math.ceil(count / page_size), count


def validate_file_size(file_body, file_size=1e7):
    if len(file_body) < 1e7:
        return True
    return False


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
