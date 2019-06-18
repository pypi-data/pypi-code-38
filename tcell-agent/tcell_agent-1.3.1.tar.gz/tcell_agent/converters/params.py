from __future__ import unicode_literals

from future.utils import iteritems

from tcell_agent.utils.strings import ensure_str_or_unicode

GET_PARAM = "get"
POST_PARAM = "post"
JSON_PARAM = "json"
COOKIE_PARAM = "cookies"
URI_PARAM = "uri"
HTTP_HEADER_PARAM = "header"


# source: http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression
def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def flatten_clean(encoding, param_dict, namespace=None):
    result = {}
    if namespace is None:
        namespace = tuple()

    for param_name, param_value in iteritems(param_dict or {}):
        if isinstance(param_value, dict):
            new_namespace = namespace + (ensure_str_or_unicode(encoding, param_name),)
            result = merge_two_dicts(result, flatten_clean(encoding, param_value, new_namespace))

        elif isinstance(param_value, list):
            for idx, val in enumerate(param_value):
                new_namespace = namespace + (str(idx), ensure_str_or_unicode(encoding, param_name))

                if isinstance(val, dict):
                    result = merge_two_dicts(result, flatten_clean(encoding, val, new_namespace))

                else:
                    val = ensure_str_or_unicode(encoding, val)
                    param_type = str(type(val))

                    # have to do it this way because unicode class does not exist in python3
                    # so isinstance check can't be used
                    if param_type.startswith("<class 'str'") or \
                            param_type.startswith("<type 'str'") or \
                            param_type.startswith("<type 'unicode'"):
                        result[new_namespace] = val

        else:
            param_value = ensure_str_or_unicode(encoding, param_value)
            param_type = str(type(param_value))

            # have to do it this way because unicode class does not exist in python3
            # so isinstance check can't be used
            if param_type.startswith("<class 'str'") or \
                    param_type.startswith("<type 'str'") or \
                    param_type.startswith("<type 'unicode'"):
                new_key = namespace + (ensure_str_or_unicode(encoding, param_name),)
                result[new_key] = param_value

    return result
