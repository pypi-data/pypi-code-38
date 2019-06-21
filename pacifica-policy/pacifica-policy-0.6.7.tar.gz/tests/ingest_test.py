#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the uploader policy."""
from os.path import join
from json import dumps, loads
from cherrypy.test import helper
from common_test import CommonCPSetup


class TestIngestPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the uploader policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_queries(self):
        """Test posting the queries."""
        valid_query = loads(
            open(join('test_files', 'ingest_base_query.json')).read())
        ret_data = self.get_json_page('/ingest', valid_query)
        self.assertFalse(ret_data is None)
        self.assertTrue('status' in ret_data)
        self.assertEqual(ret_data['status'], 'success')

        # change project to valid but he's an admin so this works
        valid_query[4]['key'] = 'Tag'
        valid_query[2]['value'] = '1234a'
        self.get_json_page('/ingest', valid_query)

        # change the project to be invalid => fails
        invalid_query = loads(
            open(join('test_files', 'ingest_base_query.json')).read())
        invalid_query[2]['value'] = '12'
        self.getPage('/ingest',
                     self.headers +
                     [('Content-Length', str(len(dumps(invalid_query))))],
                     'POST',
                     dumps(invalid_query))
        self.assertStatus('412 Precondition Failed')
        ret_data = loads(self.body.decode('UTF-8'))
        self.assertFalse(ret_data is None)
        self.assertTrue('message' in ret_data)

        # change instrument to be invalid => fails
        invalid_query = loads(
            open(join('test_files', 'ingest_base_query.json')).read())
        invalid_query[3]['value'] = 4321
        self.getPage('/ingest',
                     self.headers +
                     [('Content-Length', str(len(dumps(invalid_query))))],
                     'POST',
                     dumps(invalid_query))
        self.assertStatus('412 Precondition Failed')
        ret_data = loads(self.body.decode('UTF-8'))
        self.assertFalse(ret_data is None)
        self.assertTrue('message' in ret_data)

        # change the query so that the instrument xrefs and project xrefs fail (but for valid base entities)
        invalid_query = loads(
            open(join('test_files', 'ingest_base_query.json')).read())
        invalid_query[3]['value'] = 74  # instrument
        invalid_query[2]['value'] = u'1234c\u00e9'  # project
        invalid_query[1]['value'] = 12  # submitter
        self.getPage('/ingest',
                     self.headers +
                     [('Content-Length', str(len(dumps(invalid_query))))],
                     'POST',
                     dumps(invalid_query))
        self.assertStatus('412 Precondition Failed')
        ret_data = loads(self.body.decode('UTF-8'))
        self.assertFalse(ret_data is None)
        self.assertTrue('message' in ret_data)

        del valid_query[1]
        self.getPage('/ingest',
                     self.headers +
                     [('Content-Length', str(len(dumps(valid_query))))],
                     'POST',
                     dumps(valid_query))
        self.assertStatus('412 Precondition Failed')
