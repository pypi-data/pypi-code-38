from tcell_agent.utils.compat import a_string


def ensure_str_or_unicode(encoding, value):
    if isinstance(value, bytes):
        try:
            if encoding:
                return value.decode(encoding)
            return value.decode("ISO-8859-1")
        except UnicodeDecodeError:
            return value.decode("ISO-8859-1")
    elif a_string(value):
        return value
    else:
        return str(value)


def ensure_string(value):
    if a_string(value):
        return ensure_str_or_unicode("utf-8", value)

    return str(value)


def stringify(value):
    if not a_string(value):
        return str(value)
    return value
