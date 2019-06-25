from functools import reduce

#avoid safe edge issues
def deep_get(dictionary, *keys):
    val = reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) \
        else (d[key] if isinstance(d, list) and isinstance(key, int) and len(d) > key else None), keys, dictionary)
    return val
