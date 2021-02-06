# This module is used for encoding or decoding JWT token, which is not used for login

import datetime

import jwt

from app.config import JWT

SECRET = JWT["secret_key"]
ISSUER = JWT["default_iss"]


def encode_jwt(payload, expires_delta: datetime.timedelta):
    iat = datetime.datetime.utcnow()
    reserved_claims = {"iss": ISSUER, "iat": iat, "exp": iat + expires_delta}

    payload.update(reserved_claims)
    payload = {k: v for k, v in payload.items() if v is not None}
    token = jwt.encode(payload, SECRET, algorithm="HS256").decode("utf-8")
    return token


def decode_jwt(token):
    options = {"verify_exp": True, "verify_iss": True}
    return jwt.decode(
        token, SECRET, options=options, leeway=0, issuer=ISSUER, algorithms=["HS256"],
    )
