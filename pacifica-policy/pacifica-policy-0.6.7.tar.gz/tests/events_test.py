#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the events policy."""
from os.path import join
from json import loads, dumps
from cherrypy.test import helper
from common_test import CommonCPSetup


class TestEventsPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the Events policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_events_query(self):
        """Test posting the queries."""
        valid_query = loads(
            open(join('test_files', 'events_query.json')).read())
        ret_data = self.get_json_page('/events/dmlb2001', valid_query)
        self.assertFalse(ret_data is None)
        self.assertTrue('status' in ret_data)
        self.assertEqual(ret_data['status'], 'success')

    def test_bad_events_query(self):
        """Test posting the queries."""
        invalid_query = {'some': {'random': 'data'}, 'in': ['a', 'hash']}
        self.getPage('/events/dmlb2001',
                     self.headers +
                     [('Content-Length', str(len(dumps(invalid_query))))],
                     'POST',
                     dumps(invalid_query))
        self.assertStatus('412 Precondition Failed')
        self.assertHeader('Content-Type', 'application/json')
        ret_data = loads(self.body.decode('UTF-8'))
        self.assertFalse(ret_data is None)
        self.assertTrue('message' in ret_data)
        self.assertEqual(ret_data['message'], 'Precondition Failed: Invalid eventType for Not Present')
