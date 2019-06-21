#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Common server setup code for CherryPy testing."""
import logging
from json import dumps, loads
import cherrypy
from pacifica.policy.root import Root, error_page_default
from pacifica.policy.globals import CHERRYPY_CONFIG


class CommonCPSetup(object):
    """Common CherryPy setup class."""

    # pylint: disable=no-member
    def get_json_page(self, path, valid_query):
        """Get a json page and validate its return format."""
        self.getPage(path,
                     self.headers +
                     [('Content-Length', str(len(dumps(valid_query))))],
                     'POST',
                     dumps(valid_query))
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'application/json')
        return loads(self.body.decode('UTF-8'))

    @staticmethod
    def setup_server():
        """Setup each test by starting the CherryPy server."""
        logger = logging.getLogger('urllib2')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update(CHERRYPY_CONFIG)
        cherrypy.tree.mount(Root(), '/', CHERRYPY_CONFIG)
