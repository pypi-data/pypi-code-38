# encoding: utf-8

from .v0 import DummyApiV0

NAME = u'dummy'
VERSIONS = {
    0: DummyApiV0
}

# importing this package is enough to load and register the API so only export the constants.
__all__ = ['NAME',
           'VERSIONS']
