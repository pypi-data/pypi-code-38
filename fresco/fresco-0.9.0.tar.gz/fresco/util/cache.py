import sys


# Adapted from http://code.activestate.com/recipes/577969/
# Credit: Raymond Hettinger
# License: MIT
def cache_generator(original_function, maxsize):
    mapping = {}
    mapping_get = mapping.get
    root = [None, None]
    root[:] = [root, root]
    value, exc_info = None, None
    size = 0

    PREV, NEXT, KEY, VALUE = 0, 1, 2, 3
    while 1:
        key = yield value, exc_info
        link = mapping_get(key, root)
        exc_info = None
        if link is root:
            try:
                value, exc_info = original_function(key), None
            except Exception:
                exc_info = sys.exc_info()
                continue
            if size < maxsize:
                size += 1
            else:
                old_prev, old_next, old_key, old_value = root[NEXT]
                root[NEXT] = old_next
                old_next[PREV] = root
                del mapping[old_key]
            last = root[PREV]
            link = [last, root, key, value]
            mapping[key] = last[NEXT] = root[PREV] = link
        else:
            link_prev, link_next, key, value = link
            link_prev[NEXT] = link_next
            link_next[PREV] = link_prev
            last = root[PREV]
            last[NEXT] = root[PREV] = link
            link[PREV] = last
            link[NEXT] = root


def make_cache(original_function, maxsize=100):
    'Create a cache around a function that takes a single argument'
    c = cache_generator(original_function, maxsize)
    next(c)
    return c.send
