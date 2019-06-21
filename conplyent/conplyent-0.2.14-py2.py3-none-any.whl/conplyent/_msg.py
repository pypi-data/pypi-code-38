from enum import Enum


class MSGType(Enum):
    ACKNOWLEDGE = 0,
    HEARTBEAT = 1,
    COMMAND = 2,
    DETAILS = 3,
    COMPLETE = 4,
    SYNC = 5


class MSG(object):
    def __init__(self, type, request=True, **kwargs):
        self._type = type
        self._request = request
        self._kwargs = kwargs

    def __str__(self):
        string = "<MSG Type: {}> <Request?: {}>".format(self._type, self._request)
        if(self._kwargs):
            string += " <Kwargs: {}>".format(self._kwargs)
        return string

    @property
    def type(self):
        return self._type

    @property
    def request(self):
        return self._request

    @property
    def cmd_id(self):
        return self._kwargs["cmd_id"]

    @property
    def args(self):
        return self._kwargs["args"]

    @property
    def kwargs(self):
        return self._kwargs["keywargs"]

    @property
    def details(self):
        return self._kwargs["details"]

    @property
    def request_id(self):
        return self._kwargs["request_id"]

    @property
    def exit_code(self):
        return self._kwargs["exit_code"]

    @property
    def msg_num(self):
        return self._kwargs["msg_num"]

    def has_request_id(self):
        return "request_id" in self._kwargs
