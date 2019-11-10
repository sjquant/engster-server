import datetime
from .base import *  # noqa


CORS_ORIGINS = "*"
DEBUG = False

JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(999999)
