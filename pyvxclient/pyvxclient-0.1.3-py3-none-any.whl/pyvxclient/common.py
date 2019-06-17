import json


class ApiResponse(object):
    message = ""
    status_code = None
    data = None

    def __init__(self, message=None, data=None, status_code=None, ix=None):
        self.message = message
        self.status_code = status_code
        self.data = data
        self._ix = ix

    def __data__(self):
        d = {
            "message": self.message,
            "status_code": self.status_code,
            "data": self.data,
        }
        if self._ix: d['_ix'] = self._ix
        return d

    def __str__(self):
        return str(self.__data__())

    def __repr__(self):
        return str(self.__data__())

    def __dict__(self):
        return dict(self.__data__())

    def toJSON(self, indent=4, sort_keys=True):
        return json.dumps(self.__data__(), indent=indent, sort_keys=sort_keys)
