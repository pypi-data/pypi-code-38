# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import pulpcore.client.pulpcore
from pulpcore.client.pulpcore.api.workers_api import WorkersApi  # noqa: E501
from pulpcore.client.pulpcore.rest import ApiException


class TestWorkersApi(unittest.TestCase):
    """WorkersApi unit test stubs"""

    def setUp(self):
        self.api = pulpcore.client.pulpcore.api.workers_api.WorkersApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_workers_list(self):
        """Test case for workers_list

        List workers  # noqa: E501
        """
        pass

    def test_workers_read(self):
        """Test case for workers_read

        Inspect a worker  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
