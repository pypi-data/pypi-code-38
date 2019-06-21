import sys

_this_module = sys.modules[__name__]


def init(md):
    for attr_name, attr in md.__dict__.iteritems():
        setattr(_this_module, attr_name, attr)
