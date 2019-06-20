import numpy as np


def gather_wits_for_period(asset_id, start, end, limit=1800):
    from worker.data.api import API

    query = '{timestamp#gte#%s}AND{timestamp#lte#%s}' % (start, end)
    worker = API()
    wits_dataset = worker.get(
        path="/v1/data/corva", collection='wits', asset_id=asset_id, sort="{timestamp: 1}", limit=limit, query=query
    ).data

    if not wits_dataset:
        return None

    return wits_dataset


def get_config_by__id(config_collection, _id):
    from worker.data.api import API

    worker = API()
    config = worker.get(path="/v1/data/corva/%s/%s" % (config_collection, _id)).data
    return config


def is_number(data):
    """
    Check and return True if data is a number, else return False
    :param data: Input can be string, number or nan
    :return: True or False
    """
    try:
        data_cast = float(data)
        if data_cast >= 0 or data_cast <= 0:  # to make sure it is a valid number
            return True

        return False
    except ValueError:
        return False
    except TypeError:
        return False


def to_number(data):
    """
    Check and return if the data can be cast to a number, else return None
    :param data: Input can be string, number or nan
    :return: A numbers
    """
    if is_number(data):
        return float(data)

    return None


def none_to_nan(data):
    """
    If data is a list, return list with None replaced with nan.
    If data is None, return nan
    :param data:
    :return:
    """
    if isinstance(data, list):
        return [np.nan if e is None else e for e in data]

    if data is None:
        return np.nan

    return data


def get_value_from_dict(d: dict, key: str, func):
    """
    An structured way of getting data from a dict.
    :param d:
    :param key:
    :param func: the type of the data (int, str, float, ...)
    :return:
    """
    value = d.get(key, None)
    if value is not None:
        try:
            return func(value)
        except ValueError:
            pass

    return None


def is_in_and_not_none(d: dict, key: str):
    """
    An structured way of getting data from a dict.
    :param d: the dictionary
    :param key:
    :return: True or False
    """
    if key in d.keys() and d[key] is not None:
        return True

    return False


def nanround(value, decimal_places=2):
    """
    Similar to python built-in round but considering None values as well
    :param value:
    :param decimal_places:
    :return:
    """
    if is_number(value):
        return round(value, decimal_places)

    return None


def merge_dicts(d1: dict, d2: dict) -> dict:
    """
    Merge two dictionaries
    Note: the 2nd item (d2) has a higher priority to write items with similar keys
    :param d1:
    :param d2:
    :return:
    """
    d = {**d1, **d2}
    return d
