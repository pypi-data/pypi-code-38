import logging
import uuid
from functools import partial

from dli.client.exceptions import (
    CatalogueEntityNotFoundException,
    MissingMandatoryArgumentException,
    NoAccountSpecified,
)
from tests.common import SdkIntegrationTestCase

logger = logging.getLogger(__name__)


class CollectionFunctionsTestCase(SdkIntegrationTestCase):

    def setUp(self):
        super(CollectionFunctionsTestCase, self).setUp()
        self.create = partial(
            self.client.create_collection,
            name="CollectionFunctionsTestCase" + str(uuid.uuid4()),
            description="My collection description",
            manager_id="datalake-mgmt",
            documentation='This collection should be documented!',
            keywords=['test', 'abc']
        )

    def test_can_create_collection(self):
        collection = self.create()
        self.assertIsNotNone(collection)

    def test_cannot_create_collection_if_api_key_has_multiple_accounts(self):
        with self.assertRaises(NoAccountSpecified):
            self.create(manager_id=None)

    def test_edit_collection_should_unset_field_when_passed_none(self):
        collection = self.create(documentation='I have some docs')
        updated_collection = self.client.edit_collection(collection.collection_id, documentation=None)
        self.assertTrue('documentation' not in updated_collection._fields)

    def test_edit_collection_should_ignore_extra_keys_and_succeed_when_unknown_key_passed_with_kwargs(self):
        collection = self.create()
        updated_collection = self.client.edit_collection(collection.collection_id, i_do_not_exist='sabotage')
        self.assertTrue('i_do_not_exist' not in updated_collection._fields)

    def test_can_get_collection_details_by_id_or_name(self):
        collection = self.create()
        collection_by_id = self.client.get_collection(collection.collection_id)
        collection_by_id_again = self.client.get_collection(id=collection.collection_id)
        collection_by_name = self.client.get_collection(name=collection.name)

        self.assertTrue(all(c is not None for c in [collection_by_id, collection_by_id_again, collection_by_name]))
        self.assertEqual(collection_by_id.collection_id, collection_by_name.collection_id)
        self.assertEqual(collection_by_id.collection_id, collection_by_id_again.collection_id)

    def test_cannot_get_unknown_collection(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_collection('unknown')

    def test_cannot_get_collection_without_collection_id_or_name(self):
        with self.assertRaises(ValueError):
            self.client.get_collection(None)
            self.client.get_collection('')
            self.client.get_collection(id='', name='')

    def test_cannot_edit_unknown_collection(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.edit_collection('unknown')

    def test_cannot_edit_collection_without_collection_id(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.edit_collection(None)

    def test_can_edit_collection(self):
        collection = self.create()
        updated_collection = self.client.edit_collection(collection.collection_id,
                                                         description='Updated collection description')

        self.assertEqual(updated_collection.description, 'Updated collection description')
        self.assertEqual(collection.collection_id, updated_collection.collection_id)
        self.assertEqual(collection.name, updated_collection.name)
        # Collection manager still the same
        self.assertEqual(collection.manager_id, updated_collection.manager_id)

    def test_can_edit_collection_manager(self):
        collection = self.create()
        updated_collection = self.client.edit_collection(collection.collection_id, manager_id='iboxx')

        self.assertEqual(collection.collection_id, updated_collection.collection_id)
        self.assertEqual(updated_collection.manager_id, 'iboxx')

    def test_cannot_delete_unknown_collection(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.delete_collection('unknown')

    def test_cannot_delete_collection_without_collection_id(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.delete_collection(None)

    def test_can_delete_collection(self):
        collection = self.create()
        self.client.delete_collection(collection.collection_id)

        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_collection(collection.collection_id)

    def test_cannot_get_packages_for_collection_with_invalid_page_count(self):
        self.assert_page_count_is_valid_for_paginated_resource_actions(
            lambda c: self.client.get_packages_for_collection(collection_id='some_collection', count=c))

    def test_cannot_get_packages_for_unknown_collection(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_packages_for_collection('unknown')

    def test_cannot_get_packages_for_collection_without_collection_id(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.get_packages_for_collection(None)

    def test_get_packages_for_empty_collection_returns_empty_list(self):
        my_empty_collection = self.create()
        self.assertEqual(self.client.get_packages_for_collection(my_empty_collection.collection_id), [])

    def test_can_get_packages_for_collection(self):
        collection_of_my_packages = self.create()
        package_one = self.create_package('Package One', collection_ids=[collection_of_my_packages.collection_id])
        package_two = self.create_package('Package Two', collection_ids=[collection_of_my_packages.collection_id])

        my_packages = self.client.get_packages_for_collection(collection_of_my_packages.collection_id)
        self.assertEqual(len(my_packages), 2)

        my_package_ids = [p.package_id for p in my_packages]
        self.assertIn(package_one, my_package_ids)
        self.assertIn(package_two, my_package_ids)
