import datetime
import uuid
from json import dumps

from sanic.response import json


def custom_json_encoder(obj):
    """
    JSON serializer for objects not serializable by default json code
    https://stackoverflow.com/a/22238613
    """

    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError('Type %s not serializable' % type(obj))


def jsonify(*args, **kwargs):
    """
    customized json response
    ujson is only supported by linux platform

    Args:
        sanic.response.json args

    Kwargs:
        ujson: (bool) whether to use json, default: True
        sanic.response.json kwargs
    """
    ujson = kwargs.pop('ujson', True)
    if ujson:
        return json(ensure_ascii=False, *args, **kwargs)
    else:
        return json(
            default=custom_json_encoder,
            ensure_ascii=False,
            dump=dumps,
            *args,
            **kwargs)
