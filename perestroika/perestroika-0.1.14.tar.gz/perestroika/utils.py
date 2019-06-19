from django.utils.datastructures import MultiValueDict


def dict_to_multi_dict(data):
    return MultiValueDict(data)


def multi_dict_to_dict(query_dict):
    _data = {}
    query_dict = query_dict.copy()
    keys = list(query_dict.keys())

    for key in keys:
        _data[key] = query_dict.pop(key)

    return _data
