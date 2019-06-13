
import json
# import sys


class SJson:
    CLASS_MARK = '__cls__'

    @classmethod
    def to_serial(cls, o, **kwargs):
        indent = kwargs.get('indent', None)

        def default(o):
            if type(o) in [dict, list]:
                return o
            if hasattr(o, '__class__'):
                # return { **o.__dict__, '__class__': o.__class__.__name__}
                o.__dict__.update({cls.CLASS_MARK: o.__class__.__name__})
            return o.__dict__

        return json.dumps(default(o), indent=indent, default=default)

    @classmethod
    def to_deserial(cls, jstr, **kwargs):
        _globals = kwargs.get('globals', globals())

        def hook(o):
            if cls.CLASS_MARK in o:
                _cls = _globals[o[cls.CLASS_MARK]]
                # cls = getattr(sys.modules[__name__], o[cls.CLASS_MARK])
                del o[cls.CLASS_MARK]
                oc = _cls()
                oc.__dict__.update(o)
                return oc
            return o

        return json.loads(jstr, object_hook=hook)
