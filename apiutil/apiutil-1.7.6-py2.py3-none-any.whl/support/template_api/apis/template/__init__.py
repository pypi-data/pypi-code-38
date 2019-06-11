# encoding: utf-8

from .v0 import TemplateApiV0

NAME = u'template'  # could also use TemplateApiV0.PATH if its simple enough
VERSIONS = {
    0: TemplateApiV0
}

# importing this package is enough to load and register the API so only export the constants.
__all__ = ['NAME',
           'VERSIONS']
