def cast_enum_type_to_int(enum_type, value):
    if isinstance(value, str):
        value = enum_type[value]
    elif isinstance(value, int):
        value = enum_type(value)
    if not isinstance(value, enum_type):
        raise ValueError(value)
    return value.value
