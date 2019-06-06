#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface IngestAPI."""
from json import loads
import requests
from dateutil import parser
from . import CPCommonTest


class TestFileInfoAPI(CPCommonTest):
    """Test the ObjectInfoAPI class."""

    __test__ = True

    def _get_file_info(self, file_id_list):
        header_list = {'Content-Type': 'application/json'}
        req = requests.post(
            url='{0}/fileinfo/file_details/'.format(self.url),
            json=file_id_list,
            headers=header_list
        )
        return req

    def _get_earliest_latest(self, item_type, id_list, time_basis):
        header_list = {'Content-Type': 'application/json'}
        req = requests.post(
            url='{0}/fileinfo/earliest_latest/{1}/{2}/'.format(
                self.url, item_type, time_basis
            ),
            json=id_list,
            headers=header_list
        )
        return req

    def _get_files_with_tkv(self, key, value):
        header_list = {'Content-Type': 'application/json'}
        req = requests.get(
            url='{0}/fileinfo/files_for_keyvalue/{1}/{2}'.format(
                self.url, key, value
            ),
            headers=header_list
        )
        return req

    def test_fileinfo_api(self):
        """Test the GET method."""
        # test by_user_id
        file_id_list = [103, 104]
        req = self._get_file_info(file_id_list)
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 2)

    def test_bad_fileinfo_api(self):
        """Test bad file retrievals."""
        file_id_list = [105, 106]
        req = self._get_file_info(file_id_list)
        self.assertEqual(req.status_code, 404)

    def test_earliest_latest_api(self):
        """Test valid earliest/latest functionality."""
        # test for project single project by modified time
        id_list = ['1234a']
        req = self._get_earliest_latest(
            item_type='project',
            id_list=id_list,
            time_basis='modified'
        )
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        earliest = parser.parse(req_json['earliest'])
        latest = parser.parse(req_json['latest'])
        self.assertTrue(latest >= earliest)

        # test for project single project by submitted time
        id_list = ['1234a']
        req = self._get_earliest_latest(
            item_type='project',
            id_list=id_list,
            time_basis='submitted'
        )
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        earliest = parser.parse(req_json['earliest'])
        latest = parser.parse(req_json['latest'])
        self.assertTrue(latest >= earliest)

        # test for project single project by created time
        id_list = ['1234a']
        req = self._get_earliest_latest(
            item_type='project',
            id_list=id_list,
            time_basis='created'
        )
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        earliest = parser.parse(req_json['earliest'])
        latest = parser.parse(req_json['latest'])
        self.assertTrue(latest >= earliest)

    def test_bad_earliest_latest_api(self):
        """Test invalid earliest/latest functionality."""
        # test for single nonexistent project by modified time
        id_list = ['2345a']
        req = self._get_earliest_latest(
            item_type='project',
            id_list=id_list,
            time_basis='modified'
        )
        self.assertEqual(req.status_code, 404)

        # test for single existing project with bad item_type
        id_list = ['1234a']
        req = self._get_earliest_latest(
            item_type='bob',
            id_list=id_list,
            time_basis='modified'
        )
        self.assertEqual(req.status_code, 400)

        # test for single existing project with bad time basis
        req = self._get_earliest_latest(
            item_type='project',
            id_list=id_list,
            time_basis='bob'
        )
        self.assertEqual(req.status_code, 400)

    def test_files_with_tkv(self):
        """Test fileinfo retrieval with k/v pairs."""
        key = 'temp_f'
        value = 27
        req = self._get_files_with_tkv(key, value)
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 2)

    def test_bad_files_with_tkv(self):
        """Test fileinfo retrieval with k/v pairs."""
        # nonexistent key
        key = 'temp_q'
        value = 27
        req = self._get_files_with_tkv(key, value)
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 0)

        # nonexistent value, valid key
        key = 'temp_f'
        value = 29
        req = self._get_files_with_tkv(key, value)
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 0)

        # valid key, valid value, no relations
        key = 'temp_c'
        value = 27
        req = self._get_files_with_tkv(key, value)
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 0)

        # valid key, valid value, relation, no files
        key = 'temp_f'
        value = 19
        req = self._get_files_with_tkv(key, value)
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 0)
