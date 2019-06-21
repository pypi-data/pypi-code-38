#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""This is the main policy server script."""
import cherrypy
from pacifica.policy.root import Root, error_page_default
from pacifica.policy.globals import CHERRYPY_CONFIG


cherrypy.config.update({'error_page.default': error_page_default})
# pylint doesn't realize that application is actually a callable
# pylint: disable=invalid-name
application = cherrypy.Application(Root(), '/', CHERRYPY_CONFIG)
# pylint: enable=invalid-name
