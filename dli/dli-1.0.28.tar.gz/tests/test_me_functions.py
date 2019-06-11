import logging
import os
import six

from .common import SdkIntegrationTestCase


class MeFunctionsTestCase(SdkIntegrationTestCase):
    
    def assert_my_entities_are_returned(self, func):
        self.assertGreater(len(func()), 0)
        self.assertEquals(len(func(count=1)), 1)

    def test_get_my_consumed_packages_validates_page_size(self):
        self.assert_page_count_is_valid_for_paginated_resource_actions(lambda c: self.client.get_my_consumed_packages(count=c))

    def test_my_consumed_packages_returns_my_consumed_packages(self):
        package_id = self.create_package('test_consumed_packages', access="Unrestricted")
        package = self.client._get_package(package_id=package_id)
        package.request_access(
            accountId='iboxx',
            operation='request',
            comment='Hello there!'
        )
        self.assert_my_entities_are_returned(self.client.get_my_consumed_packages)

    def test_get_my_packages_validates_page_size(self):
        self.assert_page_count_is_valid_for_paginated_resource_actions(lambda c: self.client.get_my_packages(count=c))

    def test_get_my_packages_returns_packages(self):
        self.create_package("test_me_functions")
        self.assert_my_entities_are_returned(self.client.get_my_packages)

    def test_get_my_collections_validates_page_size(self):
        self.assert_page_count_is_valid_for_paginated_resource_actions(lambda c: self.client.get_my_collections(count=c))

    def test_get_my_collections_returns_collections(self):
        self.create_collection("test_get_my_collection_returns_collections")
        self.assert_my_entities_are_returned(self.client.get_my_collections)