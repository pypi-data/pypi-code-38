#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ingest with httpretty."""
from os.path import join
from json import loads
import httpretty
from pacifica.policy.ingest.rest import IngestPolicy
from uploader_policy_test import TestUploader


class TestIngest(TestUploader):
    """Test the ingest policy with httpretty."""

    @httpretty.activate
    def test_failed_admin_id(self):
        """override this to test valid query."""
        super(TestIngest, self).test_failed_admin_id()
        valid_query = loads(
            open(join('test_files', 'ingest_base_query.json')).read())
        ipolicy = IngestPolicy()
        # pylint: disable=no-member
        # pylint: disable=protected-access
        ret = ipolicy._valid_query(valid_query)
        self.assertTrue(ret)
        valid_query[1]['value'] = 100
        valid_query[2]['value'] = u'1234b\u00e9'
        ret = ipolicy._valid_query(valid_query)
        self.assertTrue(ret)
        # pylint: enable=protected-access
        # pylint: enable=no-member
