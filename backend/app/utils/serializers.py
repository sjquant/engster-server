import json
import datetime
import uuid


def json_serial(obj):
    """ 
    JSON serializer for objects not serializable by default json code 
    https://stackoverflow.com/a/22238613
    """

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError("Type %s not serializable" % type(obj))
