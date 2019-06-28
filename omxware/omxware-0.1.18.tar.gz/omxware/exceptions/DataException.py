"""
Data Service Exception
"""
from omxware.exceptions.Error import Error


class EntityNotFound(Error):
    pass


class InvalidParameter(Exception):
    pass


class NotAuthorized(Exception):
    pass


class ServerError(Exception):
    pass
