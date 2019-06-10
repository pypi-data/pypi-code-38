def as_list(value):
    if not isinstance(value, list):
        return list(value)

    return value
