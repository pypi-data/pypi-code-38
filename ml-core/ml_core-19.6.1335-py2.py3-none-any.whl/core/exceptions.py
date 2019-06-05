# -*- coding: utf-8 -*-


class MissingLinkException(Exception):
    pass


class NonRetryException(MissingLinkException):
    pass


class AccessDenied(NonRetryException):
    pass


class NotFound(NonRetryException):
    pass
