import json
import datetime
import uuid

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
    raise TypeError("Type %s not serializable" % type(obj))


def jsonify(*arg, **kwargs):
    return json(default=custom_json_encoder, *arg, **kwargs)
