#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface SummaryInfoAPI."""
import datetime
from os.path import realpath
from json import loads
import requests
from . import CPCommonTest


class TestSummaryTkvAPI(CPCommonTest):
    """Test the SummaryInfoAPI class."""

    __test__ = True

    def test_tkvinfo_insert(self):
        """Test various aspects of the tkvalue interface."""
        path = realpath('test_files')
        insert_data = loads(open(
            '{0}/{1}.json'.format(
                path,
                'tkv_upload_test'
            )
        ).read())

        header_list = {'Content-Type': 'application/json'}
        req = requests.post(
            url='{0}/tkvupload/upload_entries'.format(self.url),
            json=insert_data,
            headers=header_list
        )
        self.assertEqual(req.status_code, 200)
        self.assertTrue('success' in req.text)

        # Test value retrieval
        getreq = requests.get(
            url='{0}/tkvinfo/values_for_key/{1}'.format(
                self.url, 'organism_name'
            ),
            headers=header_list
        )
        results_obj = loads(getreq.text)
        self.assertEqual(getreq.status_code, 200)
        self.assertTrue(results_obj)

        # Test value retrieval
        getreq = requests.get(
            url='{0}/tkvinfo/values_for_key/{1}/{2}'.format(
                self.url, 'organism_name', datetime.datetime.now().replace(microsecond=0).isoformat()
            ),
            headers=header_list
        )
        results_obj = loads(getreq.text)
        self.assertEqual(getreq.status_code, 200)
        self.assertFalse(results_obj)

        # Test value retrieval
        getreq = requests.get(
            url='{0}/tkvinfo/values_for_key/{1}?end_time={2}'.format(
                self.url, 'organism_name', 'Mon Jul 12 00:00:00 2017'
            ),
            headers=header_list
        )
        results_obj = loads(getreq.text)
        self.assertEqual(getreq.status_code, 200)
        self.assertTrue(len(results_obj) == 1)

        # Test value retrieval
        getreq = requests.get(
            url='{0}/tkvinfo/values_for_key/{1}/{2}/{3}'.format(
                self.url, 'organism_name',
                'Mon Jul 5 00:00:00 2017', 'Mon Jul 12 00:00:00 2017'
            ),
            headers=header_list
        )
        results_obj = loads(getreq.text)
        self.assertEqual(getreq.status_code, 200)
        self.assertTrue(len(results_obj) == 1)

        # Test value retrieval
        getreq = requests.get(
            url='{0}/tkvinfo/values_for_key/{1}/{2}/{3}'.format(
                self.url, 'organism_name',
                'Mon Jul 12 00:00:00 2017', 'Mon Jul 5 00:00:00 2017'
            ),
            headers=header_list
        )
        results_obj = loads(getreq.text)
        self.assertEqual(getreq.status_code, 500)

        # Test value retrieval
        getreq = requests.get(
            url='{0}/tkvinfo/values_for_key/{1}/{2}'.format(
                self.url, 'organism_name', 'Mon Jul 2 00:00:00 2017'
            ),
            headers=header_list
        )
        results_obj = loads(getreq.text)
        self.assertEqual(getreq.status_code, 200)
        self.assertTrue(len(results_obj) == 2)

        badreq = requests.get(
            url='{0}/tkvinfo/values_for_key/{1}'.format(
                self.url, 'omics.dms.unclebob'
            ),
            headers=header_list
        )
        bad_results_obj = loads(badreq.text)
        self.assertEqual(getreq.status_code, 200)
        self.assertFalse(bad_results_obj)

        transaction_id = 67
        header_list = {'Content-Type': 'application/json'}

        req = requests.get(
            url='{0}/tkvinfo/kv_for_transaction/{1}'.format(
                self.url, transaction_id
            ),
            headers=header_list
        )
        results_obj = loads(req.text)
        self.assertEqual(req.status_code, 200)
        self.assertTrue(len(results_obj) > 0)
