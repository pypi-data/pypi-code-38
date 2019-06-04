from functools import wraps


class classorinstancemethod(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, ob=None, obtype=None):

        @wraps(self.func)
        def decorated(*args, **kwargs):
            selfarg = ob if ob is not None else obtype
            return self.func(selfarg, *args, **kwargs)

        return decorated
