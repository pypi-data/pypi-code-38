from typing import Optional
from raven import Client
from datalogue.version import __version__
import os

client = Client(
    dsn=os.environ.get('SENTRY_DSN'),
    include_paths=[__name__.split('.', 1)[0]],
    release=__version__)

class DtlError(Exception):

    def __init__(self, message: str, cause: Optional['DtlError'] = None):
        # Call the base class constructor with the parameters it needs
        super(DtlError, self).__init__(message)
        self.message = message
        self.cause = cause
        client.captureMessage(message)

    def __eq__(self, other: 'DtlError'):
        if isinstance(self, other.__class__):
            return self.message == other.message
        return False 


def _enum_parse_error(enum_description: str, string: str) -> str:
    return "'%s' is not a valid %s" % (string, enum_description)


def _property_not_found(property_name: str, obj: dict) -> DtlError:
    return DtlError(f"Could not find '{property_name}' in the dictionary: {obj!r}")


def _invalid_property_type(property_name: str, expected: str, obj: dict) -> DtlError:
    return DtlError(f"Property '{property_name}' was expected to be '{expected}' in {obj!r}")
