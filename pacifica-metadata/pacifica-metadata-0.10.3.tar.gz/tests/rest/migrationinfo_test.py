#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface MigrationInfo."""
import requests
from . import CPCommonTest


class TestMigrationInfoAPI(CPCommonTest):
    """Test the MigrationInfoAPI class."""

    __test__ = True

    def test_migrationinfo_api(self):
        """Test the GET method."""
        header_list = {'Content-Type': 'application/json'}

        # test instrument lookup for migration assistance
        url = '{0}/migrate/instruments/'.format(self.url)
        req = requests.get(url=url, headers=header_list)
        self.assertEqual(req.status_code, 200)

        # test user lookup for migration assistance
        url = '{0}/migrate/users/'.format(self.url)
        req = requests.get(url=url, headers=header_list)
        self.assertEqual(req.status_code, 200)

        url = '{0}/migrate/projects/'.format(self.url)
        req = requests.get(url=url, headers=header_list)
        self.assertEqual(req.status_code, 200)
