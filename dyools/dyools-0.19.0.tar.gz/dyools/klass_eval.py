from __future__ import (absolute_import, division, print_function, unicode_literals)

from past.builtins import basestring


class Eval(object):
    def __init__(self, data, context={}):
        self.data = data
        self.context = context or {}

    def eval(self, eval_result=True, keep_classes=False):
        def parse(value, ctx):
            if isinstance(value, (tuple, list)):
                return [parse(item, ctx) for item in value]
            elif isinstance(value, dict):
                _d = {}
                for _k, _v in value.items():
                    _d[parse(_k, ctx)] = parse(_v, ctx)
                return _d
            elif isinstance(value, basestring):
                res = value.format(**ctx)
                if eval_result:
                    try:
                        old = eval(res, ctx)
                        if (isinstance(old, type) and keep_classes) or not isinstance(old, type):
                            res = old
                    except Exception as e:
                        pass
                return res
            else:
                return value

        return parse(self.data, self.context)
