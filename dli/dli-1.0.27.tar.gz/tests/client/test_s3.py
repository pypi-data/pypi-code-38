import os
import tempfile
import mock
import six

from collections import namedtuple
from mock import patch
from unittest import TestCase, main

from dli.client.exceptions import InsufficientPrivilegesException
from dli.client.s3 import Client


class TestClient(TestCase):

    def setUp(self):
        self.patcher = patch('s3fs.S3FileSystem')
        self.mock_s3fs_instance = self.patcher.start().return_value
        self.s3_client = Client('dummy_key', 'dummy_secret', 'dummy_token')
        self.s3_location = 's3_test/temp/'

    def test_upload_files_to_s3_normal(self):
        # create some dummy files
        temp_file_list = [tempfile.NamedTemporaryFile() for i in range(3)]
        temp_file_path_list = [f.name for f in temp_file_list]

        expected_s3_location_list = [{
            "path": "s3://{}{}".format(self.s3_location, os.path.basename(file)),
            "size": 0
        } for file in temp_file_path_list]

        upload_result = self.s3_client.upload_files_to_s3(temp_file_path_list, self.s3_location)
        for temp_file in temp_file_list:
            temp_file.close()

        self.assertEqual(self.mock_s3fs_instance.put.call_count, 3)
        six.assertCountEqual(self, upload_result, expected_s3_location_list)

    def test_upload_files_to_s3_for_expired_token_scenario(self):
        def mock_refresh():
            self.patcher2 = patch('s3fs.S3FileSystem')
            self.mock_s3fs_instance_2 = self.patcher2.start().return_value
            dummy_access_keys = {"access_key_id": 'dummy_key', "dataset_id": 'dummy_dataset', "secret_access_key": 'dummy_secret', "session_token": 'dummy_token'}
            return namedtuple('access_key', sorted(dummy_access_keys))(**dummy_access_keys)

        # create some dummy files
        temp_file_list = [tempfile.NamedTemporaryFile() for i in range(3)]
        temp_file_path_list = [f.name for f in temp_file_list]

        expected_s3_location_list = [{
            "path": "s3://{}{}".format(self.s3_location, os.path.basename(file)),
            "size": 0
        } for file in temp_file_path_list]

        self.mock_s3fs_instance.put.side_effect = [Exception('ExpiredToken')]
        upload_result = self.s3_client.upload_files_to_s3(temp_file_path_list, self.s3_location, mock_refresh)
        for temp_file in temp_file_list:
            temp_file.close()

        self.assertEqual(self.mock_s3fs_instance.put.call_count, 1)
        self.assertEqual(self.mock_s3fs_instance_2.put.call_count, 3)
        six.assertCountEqual(self, upload_result, expected_s3_location_list)
        self.patcher2.stop()

    def test_upload_files_with_no_bucket_access_fails(self):
        self.mock_s3fs_instance.put.side_effect = [OSError(None, 'AccessDenied')]

        with self.assertRaises(InsufficientPrivilegesException):
            self.s3_client.upload_files_to_s3([os.path.relpath(__file__)], self.s3_location)

    def tearDown(self):
        self.patcher.stop()


if __name__ == '__main__':
    main()
