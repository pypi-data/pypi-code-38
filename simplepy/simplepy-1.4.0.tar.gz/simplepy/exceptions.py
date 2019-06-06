# -*- coding: utf-8 -*-

class CommonException(Exception):
    _STATUS_CODE = None

    def __init__(self, status):
        self.status = status or self._STATUS_CODE


class StringError(CommonException):
    pass


class FileError(CommonException):
    pass


class ConvertError(CommonException):
    pass
