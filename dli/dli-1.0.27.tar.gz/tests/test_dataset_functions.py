import logging
import six
import pytest

from .common import SdkIntegrationTestCase
from dli.client import builders
from dli.client.exceptions import (
    CatalogueEntityNotFoundException,
    MissingMandatoryArgumentException,
    DownloadFailed,
    InvalidPayloadException,
)


class DatasetFunctionsTestCase(SdkIntegrationTestCase):

    def setUp(self):
        super(DatasetFunctionsTestCase, self).setUp()

        self.package_id = self.create_package("test_dataset_functions")
        self.builder = self.dataset_builder(self.package_id, "test_dataset_functions")

    def create_datalake_dataset(self):
        return self.register_s3_dataset(
            package_id=self.package_id,
            dataset_name="test_dataset_functions",
            bucket_name="my-happy-bucket"
        )

    def test_get_unknown_dataset_raises_dataset_not_found_error(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_dataset("unknown")

    def test_cannot_get_dataset_without_dataset_id_or_name(self):
        with self.assertRaises(ValueError):
            self.client.get_dataset(None)

    def test_can_get_dataset_by_id_or_name(self):
        builder = self.builder.with_external_storage(
            location="jdbc://connectionstring:1232/my-db"
        )
        package = self.client.get_package(id=self.package_id)
        expected = self.client.register_dataset(builder)
        actual = self.client.get_dataset(expected.dataset_id)

        self.assertEqual(expected, actual)

        # By id
        dataset_by_id = self.client.get_dataset(id=expected.dataset_id)
        self.assertEqual(expected, dataset_by_id)

        # By name and package id
        dataset_by_name_and_package_id = self.client.get_dataset(name=expected.name, package_id=package.package_id)
        self.assertEqual(expected, dataset_by_name_and_package_id)

        # By name and package name
        dataset_by_name_and_package_name = self.client.get_dataset(name=expected.name, package_name=package.name)
        self.assertEqual(expected, dataset_by_name_and_package_name)

        # By name and package name and package id
        dataset_by_name_and_package_name_and_id = self.client.get_dataset(name=expected.name,
                                                                          package_id=package.package_id,
                                                                          package_name=package.name)
        self.assertEqual(expected, dataset_by_name_and_package_name_and_id)

    def test_cannot_get_dataset_by_name_if_package_id_and_package_name_mismatch(self):
        builder = self.builder.with_external_storage(
            location="jdbc://connectionstring:1232/my-db"
        )
        package = self.client.get_package(id=self.package_id)
        dataset = self.client.register_dataset(builder)

        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_dataset(name=dataset.name, package_id=package.package_id, package_name="unknown")
            self.client.get_dataset(name=dataset.name, package_id="unknown", package_name=package.name)

    def test_retrieve_keys_for_unknown_dataset_raises_error(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_s3_access_keys_for_dataset("unknown")

    def test_retrieve_keys_must_pass_at_least_one_dataset(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.get_s3_access_keys_for_dataset()

    def test_can_retrieve_keys_for_single_dataset(self):
        dataset = self.create_datalake_dataset()
        keys = self.client.get_s3_access_keys_for_dataset(dataset.dataset_id)

        self.assertIsNotNone(keys.access_key_id)
        self.assertIsNotNone(keys.session_token)
        self.assertIsNotNone(keys.secret_access_key)

    def test_can_retrieve_keys_for_multiple_datasets(self):
        dataset1 = self.register_s3_dataset(
            package_id=self.package_id, dataset_name="dataset1", bucket_name="my-happy-bucket-1"
        )
        dataset2 = self.register_s3_dataset(
            package_id=self.package_id, dataset_name="dataset2", bucket_name="my-happy-bucket-2"
        )

        keys = self.client.get_s3_access_keys_for_dataset(
            dataset1.dataset_id,
            dataset2.dataset_id
        )

        self.assertIsNotNone(keys.access_key_id)
        self.assertIsNotNone(keys.session_token)
        self.assertIsNotNone(keys.secret_access_key)

    def test_can_not_create_dataset_without_location(self):
        with self.assertRaises(Exception):
            self.client.register_dataset(self.builder)

    def test_can_create_dataset_with_other_location(self):
        builder = self.builder.with_external_storage(
            location="jdbc://connectionstring:1232/my-db"
        )
        dataset = self.client.register_dataset(builder)

        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.description, self.builder.payload["description"])
        self.assertEqual(dataset.location.type, "Other")

    def test_can_create_dataset_with_external_bucket(self):
        dataset = self.register_s3_dataset(self.package_id, "test_dataset", "my-happy-external-bucket")

        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.location.type, "S3")
        self.assertEqual(dataset.location.bucket, "my-happy-external-bucket")

    def test_can_edit_dataset_with_same_values(self):
        dataset = self.create_datalake_dataset()

        updated = self.client.edit_dataset(
            dataset.dataset_id,
            name=dataset.name,
            description=dataset.description,
            content_type=dataset.content_type,
            data_format=dataset.data_format
        )

        self.assertEqual(dataset.dataset_id, updated.dataset_id)
        self.assertEqual(dataset.package_id, updated.package_id)
        self.assertEqual(dataset.name, updated.name)
        self.assertEqual(dataset.location, updated.location)
        self.assertEqual(dataset.created_at, updated.created_at)
        # updated has changed
        self.assertNotEqual(dataset.updated_at, updated.updated_at)

    def test_edit_dataset_should_ignore_extra_keys_and_succeed_when_unknown_key_passed_with_kwargs(self):
        dataset = self.client.register_dataset(
            self.dataset_builder(
                self.package_id,
                dataset_name='test_ignoring_unknown_keys',
                naming_convention="naming convention",
                documentation="documentation"
            ).with_external_storage("Other")
        )
        updated_dataset = self.client.edit_dataset(dataset.dataset_id, i_do_not_exist='sabotage')
        self.assertTrue('i_do_not_exist' not in updated_dataset._fields)

    def test_edit_dataset_should_unset_field_when_passed_none(self):
        dataset = self.client.register_dataset(
            self.dataset_builder(
                self.package_id,
                dataset_name='test_removing_optional_fields',
                naming_convention="naming convention",
                documentation="documentation"
            ).with_external_storage("Other")
        )

        updated_dataset = self.client.edit_dataset(
            dataset.dataset_id,
            naming_convention=None,
            documentation=None
        )

        self.assertTrue('naming_convention' not in updated_dataset._fields)
        self.assertTrue('documentation' not in updated_dataset._fields)

    def test_can_edit_and_change_values(self):
        dataset = self.create_datalake_dataset()
        # change location to other
        builder = builders.DatasetLocationBuilder().with_external_storage("changing-location")

        updated = self.client.edit_dataset(
            dataset.dataset_id,
            location_builder=builder,
            description="new desc",
            content_type="content type",
            keywords=["test", "2"],
            load_type="Full Load"
        )

        self.assertEqual(updated.dataset_id, dataset.dataset_id)
        self.assertEqual(updated.package_id, dataset.package_id)
        self.assertEqual(updated.name, dataset.name)
        self.assertEqual(updated.description, "new desc")
        self.assertEqual(updated.content_type, "content type")
        self.assertEqual(updated.keywords, ["test", "2"])
        self.assertEqual(updated.location.type, "Other")
        self.assertEqual(updated.load_type, "Full Load")

    def test_edit_dataset_checks_location_builder_type(self):
        dataset = self.create_datalake_dataset()
        builder = builders.DatasetLocationBuilder().with_external_storage("changing-location")
        self.client.edit_dataset(
            dataset.dataset_id,
            description="new desc",
            content_type="content type",
            keywords=["test", "2"],
            load_type="Full Load",
        )

        with pytest.raises(TypeError):
            self.client.edit_dataset(
                dataset.dataset_id,
                location_builder='',
            )


    def test_can_create_dataset_with_load_type(self):
        dataset = self.client.register_dataset(builders.DatasetBuilder(
            package_id=self.package_id,
            name="dataset_with_load_type",
            description="a testing dataset",
            content_type="Pricing",
            data_format="CSV",
            publishing_frequency="Daily",
            taxonomy=[],
            load_type="Incremental Load"
        ).with_external_storage("test")
                                               )

        self.assertEqual(dataset.load_type, "Incremental Load")

    def test_can_delete_dataset(self):
        dataset = self.create_datalake_dataset()
        # delete
        self.client.delete_dataset(dataset.dataset_id)

        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_dataset(dataset.dataset_id)

    def test_delete_unknown_dataset_raises_error(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.delete_dataset("unknown")

    def test_register_dataset_in_unknown_package_raises_error(self):
        builder = builders.DatasetBuilder(
            package_id="unknown",
            name="test",
            description="a testing dataset",
            content_type="Pricing",
            data_format="CSV",
            publishing_frequency="Daily",
            taxonomy=[]
        )
        builder = builder.with_external_storage("s3://my-happy-bucket")

        with self.assertRaises(InvalidPayloadException):
            self.client.register_dataset(builder)


class DatasetDatafilesTestCase(SdkIntegrationTestCase):

    def setUp(self):
        super(DatasetDatafilesTestCase, self).setUp()

    def test_get_dataset_datafiles_raises_exception_if_dataset_does_not_exists(self):
        with self.assertRaises(Exception):
            self.client.get_datafiles("unknown")

    def test_get_dataset_datafiles_returns_empty_when_no_datafiles(self):
        package_id = self.create_package(
            name="test_get_dataset_datafiles_returns_empty_when_no_datafiles"
        )
        dataset = self.client.register_dataset(
            self.dataset_builder(
                package_id,
                "test_get_dataset_datafiles_returns_empty_when_no_datafiles"
            ).with_external_storage(location="jdbc://connectionstring:1232/my-db")
        )
        datafiles = self.client.get_datafiles(dataset.dataset_id)
        self.assertEqual(datafiles, [])

    def test_get_dataset_datafiles_returns_datafiles_for_dataset(self):
        files = [{'path': "/path/to/file/A", 'size': 99999}, {'path': "/path/to/file/B", 'size': 88888}]
        package_id = self.create_package(
            name="test_get_dataset_datafiles_returns_datafiles_for_dataset"
        )
        dataset = self.client.register_dataset(
            self.dataset_builder(
                package_id,
                "test_get_dataset_datafiles_returns_datafiles_for_dataset"
            ).with_external_storage(location="jdbc://connectionstring:1232/my-db")
        )

        for i in range(1, 4):
            self.client.register_datafile_metadata(
                dataset.dataset_id,
                "datafile %s" % i,
                files,
                data_as_of="2018-10-1%s" % i
            )

        datafiles = self.client.get_datafiles(dataset.dataset_id)
        self.assertEqual(len(datafiles), 3)

        datafiles_paged = self.client.get_datafiles(dataset.dataset_id, count=2)
        self.assertEqual(len(datafiles_paged), 2)

        # Other Lookup scenarios
        datafiles_search_by_as_of_date = self.client.get_datafiles(dataset.dataset_id, as_of_date_start='2018-10-12')
        self.assertEqual(len(datafiles_search_by_as_of_date), 2)
        self.assertTrue(all(df.name in ["datafile 2", "datafile 3"] for df in datafiles_search_by_as_of_date))

        datafiles_search_by_as_of_date = self.client.get_datafiles(dataset.dataset_id, as_of_date_end='2018-10-12')
        self.assertEqual(len(datafiles_search_by_as_of_date), 2)
        self.assertTrue(all(df.name in ["datafile 1", "datafile 2"] for df in datafiles_search_by_as_of_date))

        datafiles_search_by_as_of_date = self.client.get_datafiles(dataset.dataset_id, as_of_date_start='2018-10-10',
                                                                   as_of_date_end='2018-10-11')
        self.assertEqual(len(datafiles_search_by_as_of_date), 1)
        self.assertTrue(all(df.name == "datafile 1" for df in datafiles_search_by_as_of_date))

        datafiles_search_by_as_of_date = self.client.get_datafiles(dataset.dataset_id, name_contains='datafile 2',
                                                                   as_of_date_start='2018-10-10',
                                                                   as_of_date_end='2018-10-13')
        self.assertEqual(len(datafiles_search_by_as_of_date), 1)
        self.assertTrue(all(df.name == "datafile 2" for df in datafiles_search_by_as_of_date))

    def test_get_dataset_datafiles_raises_exception_for_invalid_as_of_date_params(self):
        package_id = self.create_package(
            name="test_get_dataset_datafiles_raises_exception_for_invalid_as_of_date_params"
        )
        dataset = self.client.register_dataset(
            self.dataset_builder(
                package_id,
                "test_get_dataset_datafiles_raises_exception_for_invalid_as_of_date_params"
            ).with_external_storage(location="jdbc://connectionstring:1232/my-db")
        )

        with self.assertRaises(InvalidPayloadException):
            self.client.get_datafiles(dataset.dataset_id, as_of_date_end='blah blah')
            self.client.get_datafiles(dataset.dataset_id, as_of_date_start='blah blah')
            self.client.get_datafiles(dataset.dataset_id, as_of_date_start='11/12/2017', as_of_date_end='15/12/2017')

    def test_get_dataset_datafiles_raises_error_for_invalid_count(self):
        self.assert_page_count_is_valid_for_paginated_resource_actions(
            lambda c: self.client.get_datafiles("some_dataset", count=c))

    def test_get_latest_datafile_raises_exception_if_dataset_does_not_exists(self):
        with self.assertRaises(Exception):
            self.client.get_latest_datafile("unknown")

    def test_get_latest_datafile_raises_exception_if_dataset_has_no_datafiles(self):
        package_id = self.create_package(
            name="test_get_latest_datafile_raises_exception_if_dataset_has_no_datafiles"
        )
        dataset = self.client.register_dataset(
            self.dataset_builder(
                package_id,
                "test_get_latest_datafile_raises_exception_if_dataset_has_no_datafiles"
            ).with_external_storage(location="jdbc://connectionstring:1232/my-db")
        )

        files = [{'path': "/path/to/file/A", 'size': 99999}, {'path': "/path/to/file/B", 'size': 88888}]
        for i in range(4, 0, -1):
            self.client.register_datafile_metadata(
                dataset.dataset_id,
                "datafile %s" % i,
                files,
                data_as_of="2018-10-1%s" % i
            )

        latest_datafile = self.client.get_latest_datafile(dataset.dataset_id)

        self.assertEqual(latest_datafile.name, 'datafile 4')

    def test_get_latest_datafile_returns_latest_datafile(self):
        package_id = self.create_package(
            name="test_get_latest_datafile_returns_latest_datafile"
        )
        dataset = self.client.register_dataset(
            self.dataset_builder(
                package_id,
                "test_get_latest_datafile_returns_latest_datafile"
            ).with_external_storage(location="jdbc://connectionstring:1232/my-db")
        )

        with self.assertRaises(Exception):
            self.client.get_latest_datafile(dataset.dataset_id)


class DatasetSchemasTestCase(SdkIntegrationTestCase):

    def setUp(self):
        super(DatasetSchemasTestCase, self).setUp()

        dataset = self.register_s3_dataset(
            package_id=self.create_package("test_dataset_schema_functions"),
            dataset_name="test_dataset_schema_functions",
            bucket_name="my-happy-bucket"
        )
        self.dataset_id = dataset.dataset_id

    def create_schema_payload(self, version, valid_as_of, **kwargs):
        payload = {
            'version': version,
            'valid_as_of': valid_as_of,
            'fields': [
                {
                    'name': 'field1',
                    'type': 'Int',
                    'nullable': True
                },
            ]
        }

        payload.update(**kwargs)
        return payload

    def test_cannot_register_schema_for_missing_or_unknown_dataset(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.register_schema(None, version='1a', valid_as_of='2018-10-31', type='My Type', fields=[])
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.register_schema('unknown', version='1a', valid_as_of='2018-10-31', type='My Type', fields=[])

    def test_cannot_register_schema_with_invalid_payload(self):
        my_schema_fields = [
            {
                'name': 'field1',
                'type': 'Int',
                'nullable': True
            },
        ]
        # fields cannot be empty or contain invalid field definitions 
        with self.assertRaises(InvalidPayloadException):
            self.client.register_schema(self.dataset_id, version='1a', valid_as_of='2018-10-31', fields=None)
        with self.assertRaises(InvalidPayloadException):
            self.client.register_schema(self.dataset_id, version='1a', valid_as_of='2018-10-31',
                                        fields=[{'random': 'keys'}])

        # type cannot be None or empty
        with self.assertRaises(InvalidPayloadException):
            self.client.register_schema(self.dataset_id, version='1a', valid_as_of='2018-10-31', type='',
                                        fields=my_schema_fields)
        with self.assertRaises(InvalidPayloadException):
            self.client.register_schema(self.dataset_id, version='1a', valid_as_of='2018-10-31', type=None,
                                        fields=my_schema_fields)

        # valid_as_of should be date in ISO format
        with self.assertRaises(InvalidPayloadException):
            self.client.register_schema(self.dataset_id, version='1a', valid_as_of='31/10/2018',
                                        fields=my_schema_fields)
        with self.assertRaises(InvalidPayloadException):
            self.client.register_schema(self.dataset_id, version='1a', valid_as_of='halloween', fields=my_schema_fields)

        # partitions if provided cannot be empty or contain invalid key value pairs 
        with self.assertRaises(InvalidPayloadException):
            self.client.register_schema(self.dataset_id, version='1a', valid_as_of='2018-10-31',
                                        fields=my_schema_fields, partitions=[])
        with self.assertRaises(InvalidPayloadException):
            self.client.register_schema(self.dataset_id, version='1a', valid_as_of='2018-10-31',
                                        fields=my_schema_fields, partitions=[{'random': 'keys'}])

    def test_can_register_schema(self):
        my_schema_fields = [
            {
                'name': 'field1',
                'type': 'Int',
                'nullable': True
            },
            {
                'name': 'field2',
                'type': 'Int',
                'nullable': False,
                'metadata': {
                    'random': 'keys'
                }
            },
        ]
        my_schema_partitions = [
            {
                'name': 'Who goes there?',
                'type': 'Phantom'
            }
        ]
        params = {
            'version': '1a',
            'valid_as_of': '2018-10-31',
            'type': 'My Funky Type',
            'fields': my_schema_fields,
            'partitions': my_schema_partitions,
            'description': 'My Funky Schema',
        }
        schema = self.client.register_schema(self.dataset_id, **params)
        self.assertIsNotNone(schema)
        self.assertEqual(schema.version, params['version'])
        self.assertEqual(schema.valid_as_of, params['valid_as_of'])
        self.assertEqual(schema.type, params['type'])
        self.assertEqual(len(schema.fields), 2)
        self.assertTrue(all([f['name'] in ['field1', 'field2'] for f in schema.fields]))
        self.assertEqual(len(schema.partitions), 1)

    def test_can_register_spark_schema(self):
        spark_schema = {
            'fields': [
                {
                    'metadata': {},
                    'name': 'field_1',
                    'nullable': True,
                    'type': 'string'
                },
                {
                    'metadata': {},
                    'name': 'field_2',
                    'nullable': True,
                    'type': 'long'
                }
            ],
            'type': 'struct'
        }
        schema = self.client.register_spark_schema(
            self.dataset_id,
            version='1a',
            valid_as_of='2018-10-31',
            spark_schema_json=spark_schema
        )
        self.assertIsNotNone(schema)
        self.assertEqual(schema.version, '1a')
        self.assertEqual(schema.valid_as_of, '2018-10-31')
        self.assertEqual(schema.type, spark_schema['type'])
        self.assertEqual(len(schema.fields), 2)
        self.assertTrue(all([f['name'] in ['field_1', 'field_2'] for f in schema.fields]))

    def test_cannot_get_schema_for_missing_or_unknown_dataset(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.get_schema(None)
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_schema('unknown')

    def test_cannot_get_schema_for_dataset_with_no_schemas(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_schema(self.dataset_id)

    def test_can_get_schema_by_version(self):
        payload = self.create_schema_payload('1a', '2018-10-31')
        self.client.register_schema(self.dataset_id, **payload)
        schema = self.client.get_schema(self.dataset_id, payload['version'])
        self.assertIsNotNone(schema)
        self.assertEqual(schema.version, payload['version'])

    def test_can_get_schema_without_version_returns_the_latest(self):
        payload_a = self.create_schema_payload('1a', '2018-10-31')
        payload_b = self.create_schema_payload('1b', '2018-11-05')

        self.client.register_schema(self.dataset_id, **payload_a)
        self.client.register_schema(self.dataset_id, **payload_b)

        schema = self.client.get_schema(self.dataset_id)
        self.assertIsNotNone(schema)
        self.assertEqual(schema.version, payload_b['version'])

    def test_cannot_get_schemas_for_missing_or_unknown_dataset(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.get_schemas(None)
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_schemas('unknown')

    def test_get_schemas_raises_error_for_invalid_count(self):
        self.assert_page_count_is_valid_for_paginated_resource_actions(
            lambda c: self.client.get_schemas("some_dataset", count=c))

    def test_get_schemas_returns_empty_for_dataset_with_no_schemas(self):
        self.assertEqual(self.client.get_schemas(self.dataset_id), [])

    def test_can_get_schemas_for_dataset_and_schemas_are_sorted_by_valid_as_of_date(self):
        payload_a = self.create_schema_payload('1a', '2018-10-31')
        payload_b = self.create_schema_payload('1b', '2018-11-05')
        payload_c = self.create_schema_payload('1c', '2018-11-02')

        self.client.register_schema(self.dataset_id, **payload_a)
        self.client.register_schema(self.dataset_id, **payload_b)
        self.client.register_schema(self.dataset_id, **payload_c)

        all_schemas = self.client.get_schemas(self.dataset_id)
        self.assertEqual(len(all_schemas), 3)
        self.assertEqual(all_schemas[0].version, payload_b['version'])

        fewer_schemas = self.client.get_schemas(self.dataset_id, count=2)
        self.assertEqual(len(fewer_schemas), 2)
        self.assertEqual(fewer_schemas[0].version, payload_b['version'])

    def test_cannot_delete_schema_for_missing_or_unknown_dataset(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.delete_schema(None, '1a')
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.delete_schema('unknown', '1a')

    def test_cannot_delete_schema_if_missing_or_unknown_version(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.delete_schema(self.dataset_id, None)
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.delete_schema(self.dataset_id, 'unknown')

    def test_can_delete_schema_by_version(self):
        # Create schema first
        payload = self.create_schema_payload('1a', '2018-10-31')
        self.client.register_schema(self.dataset_id, **payload)
        self.assertIsNotNone(self.client.get_schema(self.dataset_id, payload['version']))
        # Now Delete
        self.client.delete_schema(self.dataset_id, payload['version'])
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_schema(self.dataset_id, payload['version'])

    def test_cannot_edit_schema_for_missing_or_unknown_dataset(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.edit_schema(None, '1a')
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.edit_schema('unknown', '1a')

    def test_cannot_edit_schema_if_missing_or_unknown_version(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.edit_schema(self.dataset_id, None)
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.edit_schema(self.dataset_id, 'unknown')

    def test_can_edit_schema_by_version(self):
        # Create schema first
        payload = self.create_schema_payload('1a', '2018-10-31')
        self.client.register_schema(self.dataset_id, **payload)
        self.assertIsNotNone(self.client.get_schema(self.dataset_id, payload['version']))
        # Now Update valid as of
        result = self.client.edit_schema(self.dataset_id, payload['version'], valid_as_of='2018-11-05')
        self.assertEqual(result.valid_as_of, '2018-11-05')
        # Can update version too if available
        result = self.client.edit_schema(self.dataset_id, payload['version'], new_version='1b')
        self.assertEqual(result.version, '1b')
        # version now updated
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_schema(self.dataset_id, payload['version'])
