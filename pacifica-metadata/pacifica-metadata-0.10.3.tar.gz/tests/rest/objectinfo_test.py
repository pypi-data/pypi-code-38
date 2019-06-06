#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface IngestAPI."""
from json import loads
import requests
from . import CPCommonTest


class TestObjectInfoAPI(CPCommonTest):
    """Test the ObjectInfoAPI class."""

    __test__ = True

    def test_objectinfo_api_basic(self):
        """Test the GET method."""
        req = requests.get(
            '{0}/objectinfo?object_class_name=list'.format(self.url))
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertTrue('available_objects' in req_json)
        req_default = requests.get(
            '{0}/objectinfo?object_class_name=Keys'.format(self.url))
        req_explicit = requests.get(
            '{0}/objectinfo?object_class_name=Keys&operation=overview'.format(self.url))
        self.assertEqual(req_default.status_code, 200)
        self.assertEqual(req_explicit.status_code, 200)
        self.assertEqual(req_default.text, req_explicit.text)
        req_json = loads(req_default.text)
        self.assertTrue('record_count' in req_json)
        self.assertEqual(req_json['record_count'], 2)
        req = requests.get(
            '{0}/objectinfo?object_class_name=Keys&operation=hashlist'.format(self.url))
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertTrue('hash_list' in req_json)
        self.assertTrue('hash_lookup' in req_json)

    def test_objectinfo_api_complex(self):
        """Test the GET method."""
        req = requests.get(
            '{0}/objectinfo/project_user/hashlist'.format(self.url))
        self.assertEqual(req.status_code, 200)

    def test_bad_objectinfo_api(self):
        """Test the GET method with bad data."""
        req = requests.get(
            '{0}/objectinfo?object_class_name=DoesNotExist'.format(self.url))
        self.assertEqual(req.status_code, 404)
        self.assertTrue(
            "'DoesNotExist' is not a valid class object name" in req.text)
        req = requests.get('{0}/objectinfo'.format(self.url))
        self.assertEqual(req.status_code, 200)
        self.assertTrue('users' in loads(req.text))
