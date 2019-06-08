import json
from decimal import Decimal
import datetime
from collections.abc import Callable


try:
    from bson.objectid import ObjectId
except ImportError:
    # in case you're not using Mongodb
    class ObjectId(object):
        pass


class DateTimeEncoder(json.JSONEncoder):
    """
        Encodes datetimes and Decimals
        calls to_json on object if it has that method
    """

    def default(self, obj):
        try:
            if hasattr(obj, "isoformat"):
                return obj.isoformat().replace("T", " ")
            elif isinstance(obj, datetime.date):
                return str(obj)
            elif isinstance(obj, Decimal):
                return float(obj)
            elif hasattr(obj, "to_json") and isinstance(
                getattr(obj, "to_json"), Callable
            ):
                return obj.to_json()
            elif isinstance(obj, ObjectId):
                return str(obj)
            return json.JSONEncoder.default(self, obj)
        except:
            raise


#            return str(obj)


def loads(*args, **kwargs):
    """ calls json.loads """
    return json.loads(*args, **kwargs)


def dumps(o, **kwargs):
    """ calls json.loads with DateTimeEncoder """
    return json.dumps(o, cls=DateTimeEncoder, **kwargs)
