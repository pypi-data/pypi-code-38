#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test status policy methods."""
from json import loads, dumps
from cherrypy.test import helper
from common_test import CommonCPSetup


class TestReportingPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the status policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_transaction_details(self):
        """Return transaction details for a list of transactions."""
        transaction_list = [67, 68]
        user_id = 10
        url = '/reporting/transaction_details/{0}'.format(user_id)
        self.getPage(
            url,
            self.headers +
            [('Content-Length', str(len(dumps(transaction_list))))],
            'POST',
            dumps(transaction_list)
        )
        self.assertStatus('200 OK')
        ret_data = loads(self.body.decode('UTF-8'))
        self.assertFalse(ret_data is None)

    def test_transaction_summary(self):
        """Return upload summary results."""
        time_basis = 'modified'
        object_type = 'instrument'
        start_date = '2016-01-01'
        end_date = '2016-12-31'
        object_list = [54]
        user_id = 10
        url = '/reporting/transaction_summary/{0}/{1}/{2}/{3}?user={4}'.format(
            time_basis, object_type, start_date, end_date, user_id
        )
        self.getPage(
            url,
            self.headers + [('Content-Length', str(len(dumps(object_list))))],
            'POST',
            dumps(object_list)
        )
        self.assertStatus('200 OK')
        self.assertFalse(self.body is None)

        user_id = 150
        url = '/reporting/transaction_summary/{0}/{1}/{2}/{3}?user={4}'.format(
            time_basis, object_type, start_date, end_date, user_id
        )
        self.getPage(
            url,
            self.headers + [('Content-Length', str(len(dumps(object_list))))],
            'POST',
            dumps(object_list)
        )
        self.assertStatus('200 OK')
        # self.assertStatus('200 OK')
        # self.assertTrue(loads(self.body) is None)

    def test_bad_transaction_details(self):
        """Return transaction details for a list of transactions."""
        transaction_list = [67, 68]
        user_id = 150
        url = '/reporting/transaction_details/{0}'.format(user_id)
        self.getPage(
            url,
            self.headers +
            [('Content-Length', str(len(dumps(transaction_list))))],
            'POST',
            dumps(transaction_list)
        )
        self.assertStatus('200 OK')
        self.assertFalse(loads(self.body.decode('UTF-8')))
