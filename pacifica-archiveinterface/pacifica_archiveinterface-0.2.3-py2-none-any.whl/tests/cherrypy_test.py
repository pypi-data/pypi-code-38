#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
import requests
import cherrypy
from cherrypy.test import helper
from pacifica.archiveinterface.globals import CHERRYPY_CONFIG
from pacifica.archiveinterface.archive_utils import bytes_type
from pacifica.archiveinterface.rest_generator import ArchiveInterfaceGenerator, error_page_default
from pacifica.archiveinterface.backends.factory import ArchiveBackendFactory
from .common_setup_test import SetupTearDown


class ArchiveInterfaceCPTest(helper.CPWebCase, SetupTearDown):
    """Base class for all testing classes."""

    HOST = '127.0.0.1'
    PORT = 8080
    url = 'http://{0}:{1}'.format(HOST, PORT)
    headers = {'content-type': 'application/json'}

    @staticmethod
    def setup_server():
        """Bind tables to in memory db and start service."""
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update(CHERRYPY_CONFIG)
        cherrypy.tree.mount(
            ArchiveInterfaceGenerator(
                ArchiveBackendFactory().get_backend_archive('posix', '/tmp/cptests')
            ),
            '/',
            CHERRYPY_CONFIG
        )

    def test_interface(self):
        """Try a simple put and get."""
        resp = requests.put('{}/1234'.format(self.url),
                            data='The data in 1234')
        self.assertEqual(resp.status_code, 201)
        resp = requests.get('{}/1234'.format(self.url), stream=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.raw.read(), bytes_type('The data in 1234'))
        resp = requests.head('{}/1234'.format(self.url))
        self.assertEqual(resp.status_code, 204)
        resp = requests.post('{}/1234'.format(self.url))
        self.assertEqual(resp.status_code, 200)
        resp = requests.delete('{}/1234'.format(self.url))
        self.assertEqual(resp.status_code, 200)

        with open('/tmp/cptests/222', 'w') as test_fd:
            test_fd.write('this is file 222')
        resp = requests.patch(
            '{}/1235'.format(self.url),
            headers={'Content-Type': 'application/json'},
            data='{ "path": "/tmp/cptests/222" }'
        )
        self.assertEqual(resp.status_code, 200)

    def test_error_interface(self):
        """Test some error states."""
        resp = requests.get('{}/12345'.format(self.url), stream=True)
        self.assertEqual(resp.status_code, 500)
        self.assertTrue(
            'No such file or directory' in resp.json()['traceback'])
        resp = requests.delete('{}/12345'.format(self.url), stream=True)
        self.assertEqual(resp.status_code, 500)
        self.assertTrue(
            'No such file or directory' in resp.json()['traceback'])
