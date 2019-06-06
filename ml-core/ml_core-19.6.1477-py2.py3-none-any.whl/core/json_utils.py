# -*- coding: utf-8 -*-
from collections import defaultdict
import six

import json


def get_json_items(data, key_name=None):
    key_name = key_name or '_sha'

    def handle_items(items):
        for entry_key, entry_metadata in items:
            entry_metadata[key_name] = entry_key

            yield entry_metadata

    if isinstance(data, dict):
        data_gen = handle_items(data.items())
    else:  # list, generators
        data_gen = handle_items(data)

    for val in data_gen:
        yield val


def clean_system_keys(data):
    def is_system_key(key):
        return key.startswith('@')

    return {k: v for k, v in data.items() if not is_system_key(k)}


def clean_system_keys_iter(items_iter):
    for item in items_iter:
        yield clean_system_keys(item)


def multi_line_json_from_data(data, write_to=None, key_name=None):
    result = write_to or six.BytesIO()
    for i, item in enumerate(get_json_items(data, key_name=key_name)):
        item = clean_system_keys(item)
        json_str = json.dumps(item) + '\n'
        if six.PY3:
            json_str = json_str.encode()

        result.write(json_str)

    return result


def newline_json_file_from_json_file(data_file):
    json_data = json.load(data_file)
    return multi_line_json_from_data(json_data)


def normalize_item(item):
    result_item = {}

    for key, val in item.items():
        if key == 'meta':
            continue

        if not key.startswith('@'):
            key = '@' + key

        result_item[key] = val

    for key, val in item.get('meta', {}).items():
        result_item[key] = val

    return result_item


def __enum_dict_of_object(d):
    for data in d.values():
        yield data


def __enum_list_of_object(d):
    for data in d:
        yield data


def __count_dict_keys(d, enum_method):
    all_keys = defaultdict(int)
    for item in enum_method(d):
        for key in item.keys():
            all_keys[key] += 1

    return all_keys


def dict_normalize(d):
    enum_method = __enum_dict_of_object if isinstance(d, dict) else __enum_list_of_object

    all_keys = __count_dict_keys(d, enum_method)

    missing_keys = {key: total for key, total in all_keys.items() if total < len(d)}

    for item in enum_method(d):
        if len(item) == len(all_keys):
            continue

        for key in missing_keys.keys():
            if key in item:
                continue

            item[key] = None
