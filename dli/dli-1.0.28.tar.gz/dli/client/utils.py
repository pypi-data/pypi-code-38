try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # python 2 backport


def makedirs(path, exist_ok=False):
    Path(path).mkdir(parents=True, exist_ok=exist_ok)


def path_for(*parts):
    return Path(*parts)


def to_camel_case(snake_str):
    split = snake_str.split('_')
    camel_case_parts = [split[0].lower()] + [s.title() for s in split[1:]]
    return ''.join(camel_case_parts)


def to_camel_cased_dict(dictionary):
    return {to_camel_case(key): value for (key, value) in dictionary.items()}


def filter_out_unknown_keys(dictionary, keys_set):
    return {k: v for (k, v) in dictionary.items() if k in keys_set}

def ensure_count_is_valid(count):
    count = int(count)
    if count <= 0:
        raise ValueError("`count` should be a positive integer")
