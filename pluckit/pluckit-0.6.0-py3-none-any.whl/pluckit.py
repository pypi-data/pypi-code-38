import re
from types import *


__all__ = [ 'pluckit' ]



def pluckit(obj, handle):
    if obj is None or handle is None:
        # nothing to pluck
        return None

    # function pointer, behave like map()
    if callable(handle):
        return handle(obj)

    # index for list-like object
    if isinstance(handle, int):
        return obj[handle]

    # just pass it through
    if not isinstance(handle, str):
        return obj[handle]

    return __pluckPath(obj, handle)


path_regex = re.compile(
    r'^((?P<dot>\.)?(?P<handle>\*|-?\d+|[a-z_][a-z0-9_]*)|\[(?P<subscript>.+?)\])(?=[\*\.\[]|\Z)',
    flags=re.IGNORECASE
)
is_numeric = re.compile(r'^-?\d+$').match
is_slice = re.compile(r'^(-?\d+)?:(-?\d+)?:?(-?\d+)?$').match

def __pluckPath(obj, path):
    res = obj

    while path:
        match = path_regex.match(path)

        if not match:
            raise ValueError('invalid path syntax: ' + path)

        # trim element from remaining path
        path = path[len(match.group()):]

        # an explicit attribute or method
        attr = bool(match.group('dot'))

        # an explicit subscript
        subscript = bool(match.group('subscript'))

        handle = match.group('handle') or match.group('subscript')


        if '*' == handle:
            # match all values

            if hasattr(res, 'values'):
                values = res.values()
            else:
                values = iter(res)

            if path:
                # pluck remaining path from all values
                res = [ pluckit(x, path) for x in values ]

                if len(res) == 0 and not path_regex.match(path):
                    # corner case were path needs validation,
                    # eg pluckit([], '*.')
                    raise ValueError('invalid path syntax: ' + path)
            else:
                # match all remaining values
                res = list(values)

            # break out of loop since pluck completed via recursion
            return res

        elif attr:
            # explicit object attribute or method
            res = __pluckAttr(res, handle)

        elif subscript:
            # explicit subscript index, eg. for dict or list

            if is_numeric(handle):
                # list-like
                handle = int(handle)
            elif is_slice(handle):
                # slice (or range)
                handle = slice(*(int(x) if x else None for x in handle.split(':')))
            elif handle[0] == handle[-1] and (handle[0] in ['"', "'"]):
                # strip quotes
                handle = handle[1:-1]

            res = res[handle]

        else:
            # unspecified type, use heuristics.
            # only possible on first path element
            assert obj == res

            if hasattr(res, 'keys'):
                res = res[handle]

            elif hasattr(res, handle):
                # seems legit since attr exists, so go with it
                res = __pluckAttr(res, handle)

            elif hasattr(res, '__getitem__'):
                # assume handle is subscript

                if is_numeric(handle):
                    # list-like index
                    res = res[int(handle)]
                else:
                    # dict-like index
                    res = res[handle]

            else:
                raise ValueError('invalid handle: ' + handle)

    return res


def __pluckAttr(obj, handle):
    attr = getattr(obj, handle)

    # if it's a method
    if isinstance(attr, (
        BuiltinFunctionType, BuiltinMethodType,
        FunctionType, MethodType,
    )):
        # call it and use return value
        return attr()

    # otherwise, it's a class attribute
    return attr
