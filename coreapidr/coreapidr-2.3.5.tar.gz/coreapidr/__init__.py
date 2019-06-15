# coding: utf-8
from coreapidr import auth, codecs, exceptions, transports, utils
from coreapidr.client import Client
from coreapidr.document import Array, Document, Link, Object, Error, Field


__version__ = '2.3.5'
__all__ = [
    'Array', 'Document', 'Link', 'Object', 'Error', 'Field',
    'Client',
    'auth', 'codecs', 'exceptions', 'transports', 'utils',
]
