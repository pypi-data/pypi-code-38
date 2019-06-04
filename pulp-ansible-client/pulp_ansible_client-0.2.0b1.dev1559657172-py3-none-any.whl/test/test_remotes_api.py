# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import pulpcore.client.pulp_ansible
from pulpcore.client.pulp_ansible.api.remotes_api import RemotesApi  # noqa: E501
from pulpcore.client.pulp_ansible.rest import ApiException


class TestRemotesApi(unittest.TestCase):
    """RemotesApi unit test stubs"""

    def setUp(self):
        self.api = pulpcore.client.pulp_ansible.api.remotes_api.RemotesApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_remotes_ansible_ansible_create(self):
        """Test case for remotes_ansible_ansible_create

        Create an ansible remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_ansible_delete(self):
        """Test case for remotes_ansible_ansible_delete

        Delete an ansible remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_ansible_list(self):
        """Test case for remotes_ansible_ansible_list

        List ansible remotes  # noqa: E501
        """
        pass

    def test_remotes_ansible_ansible_partial_update(self):
        """Test case for remotes_ansible_ansible_partial_update

        Partially update an ansible remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_ansible_read(self):
        """Test case for remotes_ansible_ansible_read

        Inspect an ansible remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_ansible_sync(self):
        """Test case for remotes_ansible_ansible_sync

        """
        pass

    def test_remotes_ansible_ansible_update(self):
        """Test case for remotes_ansible_ansible_update

        Update an ansible remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_collection_create(self):
        """Test case for remotes_ansible_collection_create

        Create a collection remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_collection_delete(self):
        """Test case for remotes_ansible_collection_delete

        Delete a collection remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_collection_list(self):
        """Test case for remotes_ansible_collection_list

        List collection remotes  # noqa: E501
        """
        pass

    def test_remotes_ansible_collection_partial_update(self):
        """Test case for remotes_ansible_collection_partial_update

        Partially update a collection remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_collection_read(self):
        """Test case for remotes_ansible_collection_read

        Inspect a collection remote  # noqa: E501
        """
        pass

    def test_remotes_ansible_collection_sync(self):
        """Test case for remotes_ansible_collection_sync

        """
        pass

    def test_remotes_ansible_collection_update(self):
        """Test case for remotes_ansible_collection_update

        Update a collection remote  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
