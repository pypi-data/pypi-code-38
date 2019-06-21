# -*- coding: utf-8 -*-


def __get_keys(d):
    return sorted(list(d[0].keys()))


__empty_object = object()


def __get_row(obj, total_keys):
    items = []
    has_items = False
    for key in total_keys:
        val = obj.get(key, __empty_object)

        if val == __empty_object:
            val = None
        else:
            has_items = True

        items.append(val or '')

    if not has_items:
        return []

    return items


def dict_to_csv(d, fields=None):
    def get_next_obj():
        try:
            return next(items_iter)
        except StopIteration:
            return None

    if isinstance(d, dict):
        d = [d]

    total_keys = fields

    items_iter = iter(d)

    obj = get_next_obj() or {}

    if total_keys is None:
        total_keys = __get_keys([obj])

    if len(total_keys) == 0:
        return

    yield total_keys

    while True:
        row = __get_row(obj, total_keys)
        if len(row) == 0:
            break

        yield row
        obj = get_next_obj()
        if obj is None:
            break


def format_json_data(json_data, formatters=None):
    if formatters is None:
        return json_data

    for row in json_data:
        for field, formatter in formatters.items():
            if field in row:
                row[field] = formatter(row[field])

    return json_data
