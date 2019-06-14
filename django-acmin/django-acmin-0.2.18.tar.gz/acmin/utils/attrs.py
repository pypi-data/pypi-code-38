import datetime


def attr(obj, attribute, default=None):
    name = str(attribute).strip()
    result = None
    if obj is not None:
        if "." not in name:
            if isinstance(obj, dict):
                result = obj.get(name, default)
            elif isinstance(obj, (list, tuple)):
                try:
                    result = obj[int(name)]
                except Exception:
                    result = None
            elif hasattr(obj, name):
                result = getattr(obj, name)
        else:
            parts = name.split(".", 1)
            result = attr(attr(obj, parts[0]), parts[1])

    if result is None:
        result = default
    return result


def display(obj, attribute):
    result = attr(obj, attribute, default="")
    if isinstance(result, bool):
        result = "是" if result else '否'
    elif isinstance(result, datetime.datetime):
        result = result.strftime("%Y-%m-%d %H:%M:%S")
    return result
