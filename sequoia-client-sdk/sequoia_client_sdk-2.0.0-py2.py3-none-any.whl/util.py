import json

import re


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts. Supports NoneType.
    """
    result = {}
    for dictionary in dict_args:
        if dictionary:
            result.update(dictionary)
    return result


def wrap(json_str, resource_name):
    formatted_name = None
    if resource_name is not None:
        formatted_name = dash_case_to_camel_case(resource_name)
    json_object = json_str
    if not isinstance(json_object, dict):
        json_object = json.loads(json_str)
    if formatted_name is not None and formatted_name not in json_object:
        json_object = {formatted_name: json_object}
    return json.dumps(json_object)


def unwrap(json_object, resource_name):
    formatted_name = dash_case_to_camel_case(resource_name)
    unwrapped_json = json_object
    if formatted_name in json_object:
        unwrapped_json = json_object[formatted_name]
    return unwrapped_json


def dash_case_to_camel_case(resource_name):
    # Precompile expression
    return re.sub(r'(?!^)-([a-zA-Z])', lambda m: m.group(1).upper(), resource_name)


def camel_case_to_dash_ase(resource_name):
    aux = first_cap_re.sub(r'\1-\2', resource_name)
    return all_cap_re.sub(r'\1-\2', aux).lower()


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
