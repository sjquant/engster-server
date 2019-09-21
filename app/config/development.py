import datetime
from .base import *  # noqa


CORS_ORIGINS = '*'
CORS_AUTOMATIC_OPTIONS = True
DEBUG = False

JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(999999)
