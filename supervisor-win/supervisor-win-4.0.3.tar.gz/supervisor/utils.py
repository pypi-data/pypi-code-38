from functools import wraps


def raise_not_implemented(obj):
    """Raise NotImplementedError"""
    @wraps(obj)
    def __inner(*args, **kwargs):
        raise NotImplementedError(
            "{0.__name__} '{1.__name__}' not implemented!".format(
                type(obj), obj))
    return __inner
