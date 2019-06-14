from inspect import stack
import shelve

from .structure import get_cache_path

def project_cache():
    return shelve.open(get_cache_path())

def quick_cache(value=None):
    frame = stack()[1]
    identifier = f'{frame.filename}:{frame.function}'
    with project_cache() as cache:
        if value is None:
            return cache[identifier] if identifier in cache else value
        else:
            cache[identifier] = value
            return value