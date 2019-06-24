import datetime
import json as py_json


class JSONEncoder(py_json.JSONEncoder):

    def __init__(self, fail_on_unknown=False, **kwargs):
        kwargs['skipkeys'] = True
        super(JSONEncoder, self).__init__(**kwargs)

        self.fail_on_unknown = fail_on_unknown

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if self.fail_on_unknown:
            return super(JSONEncoder, self).default(obj)
        else:
            return None


class json(object):

    @staticmethod
    def loads(s, **kwargs):
        return py_json.loads(s, **kwargs)

    @staticmethod
    def dumps(obj, **kwargs):
        return py_json.dumps(obj, cls=JSONEncoder, **kwargs)

    @staticmethod
    def dump(obj, fp, **kwargs):
        return py_json.dump(obj, fp, cls=JSONEncoder, **kwargs)
