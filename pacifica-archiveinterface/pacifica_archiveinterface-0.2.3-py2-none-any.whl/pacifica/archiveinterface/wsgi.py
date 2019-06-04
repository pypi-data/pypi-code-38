#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Pacifica Archive Interface.

This is the main program that starts the WSGI server.

The core of the server code is in archive_interface.py.

Any new Backends added need to have the type argument extended
to support the new Backend Archie type

"""
from os import getenv
import cherrypy
from .rest_generator import ArchiveInterfaceGenerator, error_page_default
from .backends.factory import ArchiveBackendFactory
from .globals import CHERRYPY_CONFIG

BACKEND_TYPE = getenv('PAI_BACKEND_TYPE', 'posix')
PREFIX = getenv('PAI_PREFIX', '/tmp')

# Get the specified Backend Archive
FACTORY = ArchiveBackendFactory()
BACKEND = FACTORY.get_backend_archive(
    BACKEND_TYPE,
    PREFIX
)

cherrypy.config.update({'error_page.default': error_page_default})
# pylint doesn't realize that application is actually a callable
# pylint: disable=invalid-name
application = cherrypy.Application(
    ArchiveInterfaceGenerator(BACKEND),
    '/',
    CHERRYPY_CONFIG
)
# pylint: enable=invalid-name
