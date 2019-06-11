import re


def convert_to_str_if_unicode(val):
    return str(val) if isinstance(val, unicode) else val


def clean_unicode_of_dict(d):
    return {convert_to_str_if_unicode(k): convert_to_str_if_unicode(v)
            for k, v in d.items()}


def is_int_repr_or_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


def build_path(*args):
    return '/' + '/'.join(str(s).strip('/') for s in args)


def to_camel_case(string):
    """Give the camelCase representation of a snake_case string."""
    try:
        return re.sub(r'_(\w)', lambda x: x.group(1).upper(), string)
    except TypeError as e:
        raise ValueError(e)


def convert_key_to_camel_case(x):
    if isinstance(x, dict):
        return {to_camel_case(k): convert_key_to_camel_case(v)
                for k, v in x.items()}
    if isinstance(x, list):
        return [convert_key_to_camel_case(e) for e in x]
    return x
