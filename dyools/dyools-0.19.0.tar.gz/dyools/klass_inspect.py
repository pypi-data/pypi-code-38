from __future__ import (absolute_import, division, print_function, unicode_literals)

import inspect


class Inspect(object):
    @classmethod
    def signature(cls, callable):
        if getattr(inspect, 'signature'):
            print(inspect.signature(callable))
        if getattr(inspect, 'getargspec'):
            print(inspect.getargspec(callable))
        if getattr(inspect, 'getfullargspec'):
            print(inspect.getfullargspec(callable))

    @classmethod
    def source(cls, callable):
        print(inspect.getsource(callable))

Signature = Inspect.signature
