import sys
from .base import ClsMeta


def __getattr__(_):
    pass


class Quiet(sys.modules[__name__].__class__):
    def __call__(self, *_, **__):
        pass


sys.modules[__name__].__class__ = Quiet
