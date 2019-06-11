import boto3
import logging
import six

from .common import SdkIntegrationTestCase
from dli.client import builders
from dli.client.exceptions import (
    CatalogueEntityNotFoundException,
    MissingMandatoryArgumentException,
    InvalidPayloadException,
)

from . import localstack_helper


class AutoRegMetadataFunctionsTestCase(SdkIntegrationTestCase):

    test_topic = 's3-notifications'
    test_bucket = 'test-bucket'

    s3 = localstack_helper.get_s3_client()
    sns = localstack_helper.get_sns_client()

    @classmethod
    def setUpClass(cls):
        cls.sns.create_topic(Name=cls.test_topic)

    @classmethod
    def tearDownClass(cls):
        cls.sns.delete_topic(TopicArn=localstack_helper.get_topic_arn(cls.test_topic))

    def setUp(self):
        super(AutoRegMetadataFunctionsTestCase, self).setUp()

        self.package_id = self.create_package("test_auto_reg_metadata_functions")
        self.dataset = self.register_s3_dataset(
                self.package_id,
                "test_auto_reg_metadata_functions",
                self.test_bucket,
                "test/auto")

    def create_test_auto_reg_metadata(self, **kwargs):
        params = {
            'dataset_id': self.dataset.dataset_id,
            'path_template': 'path/to/as_of_date={{ year }}-{{ month }}-{{ day }}/type={{ type }}',
            'name_template': "Datafile_{{ type }}_{{ year }}-{{ month }}-{{ day }}",
            'as_of_date_template': "{{ year }}-{{ month }}-{{ day }}",
            'active': True,
            'sns_topic_for_s3_events': self.test_topic,
            'handle_files': False
        }

        if kwargs:
            params.update(**kwargs)

        return self.client.set_auto_registration_metadata(
            dataset_id=params['dataset_id'],
            path_template=params['path_template'],
            name_template=params['name_template'],
            as_of_date_template=params['as_of_date_template'],
            active=params['active'],
            sns_topic_for_s3_events=params['sns_topic_for_s3_events'],
            handle_files=params['handle_files']
        )

    def test_cannot_register_auto_reg_metadata_if_missing_dataset(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.create_test_auto_reg_metadata(dataset_id=None)
        with self.assertRaises(MissingMandatoryArgumentException):
            self.create_test_auto_reg_metadata(dataset_id='')

    def test_cannot_register_auto_reg_metadata_for_unknown_dataset(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.create_test_auto_reg_metadata(dataset_id='unknown')

    def assert_cannot_register_auto_reg_metadata_if_missing_mandatory_parameter(self, param_name):
        with self.assertRaises(InvalidPayloadException):
            self.create_test_auto_reg_metadata(**{param_name: None})
        with self.assertRaises(InvalidPayloadException):
            self.create_test_auto_reg_metadata(**{param_name: ''})

    def test_cannot_register_auto_reg_metadata_if_missing_path_template(self):
        self.assert_cannot_register_auto_reg_metadata_if_missing_mandatory_parameter('path_template')

    def test_cannot_register_auto_reg_metadata_if_missing_name_template(self):
        self.assert_cannot_register_auto_reg_metadata_if_missing_mandatory_parameter('name_template')

    def test_cannot_register_auto_reg_metadata_if_missing_as_of_date_template(self):
        self.assert_cannot_register_auto_reg_metadata_if_missing_mandatory_parameter('as_of_date_template')

    def test_cannot_register_auto_reg_metadata_if_missing_active_status_flag(self):
        self.assert_cannot_register_auto_reg_metadata_if_missing_mandatory_parameter('active')

    def test_cannot_register_auto_reg_metadata_if_undefined_variables_in_name_template(self):
        path_template = 'path/to/as_of_date={{ year }}-{{ month }}-{{ day }}/type={{ type }}'
        name_template = "Datafile_{{ some_undefined }}_{{ year }}-{{ month }}-{{ day }}"
        with self.assertRaises(InvalidPayloadException):
            self.create_test_auto_reg_metadata(path_template=path_template, name_template=name_template)

    def test_cannot_register_auto_reg_metadata_if_undefined_variables_in_as_of_date_template(self):
        path_template = 'path/to/as_of_date={{ year }}-{{ month }}-{{ day }}/type={{ type }}'
        as_of_date_template = "{{ some_undefined }}_{{ year }}-{{ month }}-{{ day }}"
        with self.assertRaises(InvalidPayloadException):
            self.create_test_auto_reg_metadata(path_template=path_template, as_of_date_template=as_of_date_template)

    def test_cannot_register_auto_reg_metadata_if_unused_variables_in_path_template(self):
        path_template = 'path/to/{{ unused }}/as_of_date={{ year }}-{{ month }}-{{ day }}/type={{ type }}'
        name_template = "Datafile_{{ year }}-{{ month }}-{{ day }}"
        as_of_date_template = "{{ year }}-{{ month }}-{{ day }}"
        with self.assertRaises(InvalidPayloadException):
            self.create_test_auto_reg_metadata(path_template=path_template, name_template=name_template, as_of_date_template=as_of_date_template)

    def test_cannot_register_auto_reg_metadata_for_non_s3_dataset(self):
        dataset = self.client.register_dataset(
            self.dataset_builder(
                self.package_id,
                "test_cannot_register_auto_reg_metadata_for_non_s3_dataset"
            ).with_external_storage(location="jdbc://connectionstring:1232/my-db")
        )
        with self.assertRaises(InvalidPayloadException):
            self.create_test_auto_reg_metadata(dataset_id=dataset.dataset_id)

    def test_can_register_auto_reg_metadata_for_dataset(self):
        auto_reg_metadata = self.create_test_auto_reg_metadata()
        self.assertIsNotNone(auto_reg_metadata)
        self.assertEqual(auto_reg_metadata.dataset_id, self.dataset.dataset_id)

    def test_can_edit_has_auto_reg_failure_flag(self):
        auto_reg_metadata = self.create_test_auto_reg_metadata(has_auto_registry_failure_notifications=True)
        edited_auto_reg_metadata = self.client.edit_auto_registration_metadata(
            auto_reg_metadata.auto_reg_metadata_id, has_auto_registry_failure_notifications=False
        )
        
        assert auto_reg_metadata.has_auto_registry_failure_notifications
        assert not edited_auto_reg_metadata.has_auto_registry_failure_notifications

    def test_has_auto_reg_failure_flag_should_not_change_when_set_to_none(self):
        auto_reg_metadata = self.create_test_auto_reg_metadata(has_auto_registry_failure_notifications=True)
        auto_reg_metadata = self.client.edit_auto_registration_metadata(
            auto_reg_metadata.auto_reg_metadata_id,
            has_auto_registry_failure_notifications=None
        )
        assert auto_reg_metadata.has_auto_registry_failure_notifications

    def test_cannot_get_auto_reg_metadata_if_mising_dataset_id(self):
        with self.assertRaises(ValueError):
            self.client.get_auto_registration_metadata(dataset_id='')
        with self.assertRaises(ValueError):
            self.client.get_auto_registration_metadata(dataset_id=None)

    def test_cannot_get_auto_reg_metadata_if_mising_auto_reg_metadata_id(self):
        with self.assertRaises(ValueError):
            self.client.get_auto_registration_metadata(auto_reg_metadata_id='')
        with self.assertRaises(ValueError):
            self.client.get_auto_registration_metadata(auto_reg_metadata_id=None)

    def test_cannot_get_auto_reg_metadata_if_mising_dataset_id_and_auto_reg_metadata_id(self):
        with self.assertRaises(ValueError):
            self.client.get_auto_registration_metadata(dataset_id='', auto_reg_metadata_id='')

    def test_cannot_get_auto_reg_metadata_for_unknown_dataset_id(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_auto_registration_metadata(dataset_id='unknown')

    def test_cannot_get_auto_reg_metadata_for_unknown_auto_reg_metadata_id(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_auto_registration_metadata(auto_reg_metadata_id='unknown')

    def test_cannot_get_auto_reg_metadata_for_unknown_dataset_id_and_auto_reg_metadata_id(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_auto_registration_metadata(dataset_id='unknown', auto_reg_metadata_id='unknown')

    def test_can_get_auto_reg_metadata_by_dataset_id(self):
        auto_reg_metadata = self.create_test_auto_reg_metadata()
        result = self.client.get_auto_registration_metadata(dataset_id=auto_reg_metadata.dataset_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.auto_reg_metadata_id, auto_reg_metadata.auto_reg_metadata_id)

    def test_can_get_auto_reg_metadata_by_auto_reg_metadata_id(self):
        auto_reg_metadata = self.create_test_auto_reg_metadata()
        result = self.client.get_auto_registration_metadata(auto_reg_metadata_id=auto_reg_metadata.auto_reg_metadata_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.auto_reg_metadata_id, auto_reg_metadata.auto_reg_metadata_id)

    def test_can_get_auto_reg_metadata_by_dataset_id_and_auto_reg_metadata_id(self):
        auto_reg_metadata = self.create_test_auto_reg_metadata()
        result = self.client.get_auto_registration_metadata(
                    dataset_id=auto_reg_metadata.dataset_id,
                    auto_reg_metadata_id=auto_reg_metadata.auto_reg_metadata_id
                )
        self.assertIsNotNone(result)
        self.assertEqual(result.auto_reg_metadata_id, auto_reg_metadata.auto_reg_metadata_id)

    def test_cannot_delete_auto_reg_metadata_if_missing_auto_reg_id(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.delete_auto_registration_metadata(None)
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.delete_auto_registration_metadata('')

    def test_cannot_delete_unknown_auto_reg_metadata(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.delete_auto_registration_metadata("unknown")

    def test_can_delete_auto_reg_metadata(self):
        auto_reg_metadata = self.create_test_auto_reg_metadata()
        # Delete 
        self.client.delete_auto_registration_metadata(auto_reg_metadata.auto_reg_metadata_id)
        # Try fetching the same will throw error now
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.get_auto_registration_metadata(auto_reg_metadata_id=auto_reg_metadata.auto_reg_metadata_id)

    def test_cannot_edit_auto_reg_metadata_if_missing_auto_reg_id(self):
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.edit_auto_registration_metadata(None)
        with self.assertRaises(MissingMandatoryArgumentException):
            self.client.edit_auto_registration_metadata('')

    def test_cannot_edit_unknown_auto_reg_metadata(self):
        with self.assertRaises(CatalogueEntityNotFoundException):
            self.client.edit_auto_registration_metadata("unknown")

    def test_can_edit_auto_reg_metadata(self):
        auto_reg_metadata = self.create_test_auto_reg_metadata()
        self.assertEqual(auto_reg_metadata.active, True)

        # Edit the metadata. Make it inactive for example
        edited_metadata = self.client.edit_auto_registration_metadata(
            auto_reg_metadata.auto_reg_metadata_id,
            active=False            
        )
        self.assertEqual(edited_metadata.active, False)