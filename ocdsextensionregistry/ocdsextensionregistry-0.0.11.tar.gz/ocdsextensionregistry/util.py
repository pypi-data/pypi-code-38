import json
from collections import OrderedDict


def json_loads(data):
    """
    Loads JSON data, preserving order.
    """
    return json.loads(data, object_pairs_hook=OrderedDict)
