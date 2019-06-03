# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import pulpcore.client.pulp_maven
from pulpcore.client.pulp_maven.api.distributions_api import DistributionsApi  # noqa: E501
from pulpcore.client.pulp_maven.rest import ApiException


class TestDistributionsApi(unittest.TestCase):
    """DistributionsApi unit test stubs"""

    def setUp(self):
        self.api = pulpcore.client.pulp_maven.api.distributions_api.DistributionsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_distributions_maven_maven_create(self):
        """Test case for distributions_maven_maven_create

        Create a maven distribution  # noqa: E501
        """
        pass

    def test_distributions_maven_maven_delete(self):
        """Test case for distributions_maven_maven_delete

        Delete a maven distribution  # noqa: E501
        """
        pass

    def test_distributions_maven_maven_list(self):
        """Test case for distributions_maven_maven_list

        List maven distributions  # noqa: E501
        """
        pass

    def test_distributions_maven_maven_partial_update(self):
        """Test case for distributions_maven_maven_partial_update

        Partially update a maven distribution  # noqa: E501
        """
        pass

    def test_distributions_maven_maven_read(self):
        """Test case for distributions_maven_maven_read

        Inspect a maven distribution  # noqa: E501
        """
        pass

    def test_distributions_maven_maven_update(self):
        """Test case for distributions_maven_maven_update

        Update a maven distribution  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
