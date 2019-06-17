"""
Package private common utilities. Do not use directly.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
import rockset

__all__ = [
    'Error', 'Warning', 'InterfaceError', 'DatabaseError', 'DataError',
    'OperationalError', 'IntegrityError', 'InternalError', 'ProgrammingError',
    'NotSupportedError',
]

class Warning(Exception):
    """Exception raised for important warnings like data truncations while inserting, etc."""
    pass


class Error(rockset.exception.Error):
    """Exception that is the base class of all other error exceptions. You
    can use this to catch all errors with one single except statement.
    Warnings are not considered errors and thus should not use this class as
    base.
    """
    @classmethod
    def from_rockset_exception(cls, rse, **kwargs):
        kwargs['message'] = rse.message
        kwargs['code'] = hasattr(rse, 'code') and rse.code or None
        kwargs['type'] = hasattr(rse, 'type') and rse.type or None
        if type(rse) == rockset.exception.ServerError:
            dbapi_exception = InternalError(**kwargs)
        elif type(rse) == rockset.exception.NotYetImplemented:
            dbapi_exception = NotSupportedError(**kwargs)
        elif type(rse) == rockset.exception.AuthError:
            dbapi_exception = OperationalError(**kwargs)
        elif type(rse) == rockset.exception.LimitReached:
            dbapi_exception = OperationalError(**kwargs)
        elif type(rse) == rockset.exception.ResourceSuspendedError:
            dbapi_exception = OperationalError(**kwargs)
        elif type(rse) == rockset.exception.RequestTimeout:
            dbapi_exception = OperationalError(**kwargs)
        elif type(rse) == rockset.exception.TransientServerError:
            dbapi_exception = OperationalError(**kwargs)
        elif type(rse) == rockset.exception.InputError:
            dbapi_exception = ProgrammingError(**kwargs)
        else:
            dbapi_exception = cls(**kwargs)
        return dbapi_exception


class InterfaceError(Error):
    """Exception raised for errors that are related to the database interface
    rather than the database itself.
    """
    pass


class DatabaseError(Error):
    """Exception raised for errors that are related to the database."""
    pass


class DataError(DatabaseError):
    """Exception raised for errors that are due to problems with the processed
    data like division by zero, numeric value out of range, etc.
    """
    pass


class IntegrityError(DatabaseError):
    """Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore, the transaction is out of sync, etc
    """
    pass


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore, the transaction is out of sync, etc
    """
    pass


class NotSupportedError(DatabaseError):
    """Exception raised in case a method or database API was used which is not
    supported by the database, e.g. requesting a ``.rollback()`` on a
    connection that does not support transaction or has transactions turned off
    """
    pass


class OperationalError(DatabaseError):
    """Exception raised for errors that are related to the database's
    operation and not necessarily under the control of the programmer,
    e.g. an unexpected disconnect occurs, the data source name is not found,
    a transaction could not be processed, a memory allocation error occurred
    during processing, etc.
    """
    pass


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors, e.g. table not found or
    already exists, syntax error in the SQL statement, wrong number of
    parameters specified, etc.
    """
    pass



