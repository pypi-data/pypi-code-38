# -*- coding: utf8 -*-
import os

import fudge
from botocore.stub import ANY
from fudge.inspector import arg
from google.auth import app_engine
from six import StringIO, BytesIO

from missinglink.legit.gcp_services import GCPServices, GoogleCredentialsFile
from missinglink.legit.gcs_utils import GCSDownloadDirectDownload, do_delete_all, Uploader, Downloader, s3_moniker, \
    _s3_upload_or_transfer, _az_upload_or_transfer, azure_moniker, _az_download, AzureContainerNotFound, \
    _clear_cached_objects
from tests.base import BaseTest
import httpretty


class TestGCSOperations(BaseTest):
    bucket_name = 'missinglink-public'
    s3_bucket_name = 's3://missinglink-public'
    object_name_1 = 'test_files_dont_delete/1.txt'
    s3_object_name_1 = '{bucket}/{object_name}'.format(bucket=s3_bucket_name, object_name=object_name_1)

    def setUp(self):
        super(TestGCSOperations, self).setUp()

        _clear_cached_objects()

        GoogleCredentialsFile._clear_files_cache()

    def _wrap_local_s3_auth(self, actual_test):
        def wrap():
            ACCESS_KEY = 'AWS_ACCESS_KEY_ID'
            SECRET_KEY = 'AWS_SECRET_ACCESS_KEY'

            os.environ[ACCESS_KEY] = self.some_random_shit(ACCESS_KEY)
            os.environ[SECRET_KEY] = self.some_random_shit(SECRET_KEY)

            actual_test()

        wrap()

    def _wrap_gcs_local_auth_files(self, actual_test):
        @fudge.patch('missinglink.legit.gcp_services.GoogleCredentialsFile._get_auth_config_from_default_file')
        @fudge.patch('missinglink.legit.gcp_services.GCPServices.get_default_project_id')
        def wrap(mock__get_auth_config_from_default_file, mock_get_default_project_id):
            client_secret = self.some_random_shit('client_secret')
            refresh_token = self.some_random_shit('refresh_token')
            client_id = self.some_random_shit('client_id')

            auth_info = {
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'client_id': client_id,
                'type': 'authorized_user'
            }

            mock__get_auth_config_from_default_file.expects_call().returns(auth_info)

            project_id = self.some_random_shit('project_id')

            mock_get_default_project_id.expects_call().returns(project_id)

            actual_test()

        wrap()

    def _wrap_azure_local_auth_files(self, actual_test):
        @fudge.patch('missinglink.legit.azure_config.AzureConfig._get_auth_config_from_default_file')
        def wrap(mock__get_auth_config_from_default_file, mock_get_default_project_id):
            client_secret = self.some_random_shit('client_secret')
            refresh_token = self.some_random_shit('refresh_token')
            client_id = self.some_random_shit('client_id')

            auth_info = {
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'client_id': client_id,
                'type': 'authorized_user'
            }

            mock__get_auth_config_from_default_file.expects_call().returns(auth_info)

            project_id = self.some_random_shit('project_id')

            mock_get_default_project_id.expects_call().returns(project_id)

            actual_test()

        wrap()

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.upload_from_file')
    def test_upload_bucket_gcs(self, mock_upload_from_file):
        def actual_test():
            full_path_to_data = StringIO('1234')
            content_type = self.some_random_shit('content_type')

            mock_upload_from_file.expects_call().with_args(full_path_to_data, content_type)

            bucket_name = self.some_random_shit('bucket_name')
            object_name = self.some_random_shit('object_name')

            headers = {'Content-Type': content_type}
            Uploader.upload_bucket(bucket_name, object_name, full_path_to_data, headers)

        self._wrap_gcs_local_auth_files(actual_test)

    @httpretty.activate
    def test_upload_bucket_s3(self):
        def actual_test():
            import boto3
            from botocore.stub import Stubber

            full_path_to_data = StringIO('1234')
            content_type = self.some_random_shit('content_type')

            bucket_name = self.some_random_shit('bucket_name')
            object_name = self.some_random_shit('object_name')

            s3_client = boto3.client('s3')
            stubber = Stubber(s3_client)
            expected_params = {
                'Bucket': bucket_name,
                'Key': object_name,
                'Body': ANY,
            }
            stubber.add_response('put_object', {}, expected_params)

            headers = {'Content-Type': content_type}
            with stubber:
                _s3_upload_or_transfer(s3_moniker + bucket_name, object_name, full_path_to_data, headers, s3_client=s3_client)

        self._wrap_local_s3_auth(actual_test)

    @httpretty.activate
    def test_copy_bucket_s3(self):
        def actual_test():
            import boto3
            from botocore.stub import Stubber

            full_path_to_data = self.some_random_shit('full_path_to_data')
            content_type = self.some_random_shit('content_type')

            bucket_name = self.some_random_shit('bucket_name')
            object_name = self.some_random_shit('object_name')

            s3_client = boto3.client('s3')
            stubber = Stubber(s3_client)
            expected_params = {
                'Bucket': bucket_name,
                'Key': object_name,
                'CopySource': full_path_to_data,
            }
            stubber.add_response('copy_object', {}, expected_params)

            headers = {'Content-Type': content_type}
            with stubber:
                _s3_upload_or_transfer(s3_moniker + bucket_name, object_name, s3_moniker + full_path_to_data, headers, s3_client=s3_client)

        self._wrap_local_s3_auth(actual_test)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.create_blob_from_stream')
    def test_upload_bucket_azure(self, mock_create_blob_from_stream):
        full_path_to_data = BytesIO(b'1234')
        content_type = self.some_random_shit('content_type')

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        headers = {'Content-Type': content_type}

        mock_create_blob_from_stream.expects_call().with_args(
            bucket_name, object_name, full_path_to_data, metadata={}, content_settings=arg.any())

        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_account=storage_account, storage_key=storage_key)
        _az_upload_or_transfer(azure_moniker + bucket_name, object_name, full_path_to_data, headers, fake_azure_config)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.create_blob_from_stream')
    def test_upload_bucket_azure_full_name(self, mock_create_blob_from_stream):
        full_path_to_data = BytesIO(b'1234')
        content_type = self.some_random_shit('content_type')

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        headers = {'Content-Type': content_type}

        mock_create_blob_from_stream.expects_call().with_args(
            bucket_name, object_name, full_path_to_data, metadata={}, content_settings=arg.any())

        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_key=storage_key)

        full_bucket_name = '%s.%s' % (storage_account, bucket_name)

        _az_upload_or_transfer(azure_moniker + full_bucket_name, object_name, full_path_to_data, headers, fake_azure_config)

    @httpretty.activate
    @fudge.patch('requests.head')
    @fudge.patch('requests.put')
    def test_upload_secure_url_method(self, mock_session_head, mock_session_put):
        full_path_to_data = StringIO('1234')
        content_type = self.some_random_shit('content_type')

        headers = {'Content-Type': content_type}
        head_url = self.some_random_shit('head_url')
        put_url = self.some_random_shit('put_url')

        fake_response = fudge.Fake().has_attr(status_code=404)
        mock_session_head.expects_call().with_args(head_url).returns(fake_response)

        def fake_put(url, data, headers):
            data.read(4)

            fake_put_response = fudge.Fake().has_attr(status_code=200).provides('raise_for_status')

            return fake_put_response

        mock_session_put.expects_call().with_args(put_url, data=arg.any(), headers=headers).calls(fake_put)

        Uploader.upload_http(put_url, head_url, full_path_to_data, headers)

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.download_as_string')
    def test_download_no_auth_method_with_bucket(self, mock_download_as_string):
        def actual_test():
            download_result = self.some_random_shit('result')
            mock_download_as_string.expects_call().with_args().returns(download_result)
            result = Downloader.download_bucket(self.bucket_name, self.object_name_1)
            self.assertEqual(result, download_result)

        self._wrap_gcs_local_auth_files(actual_test)

    @httpretty.activate
    def test_s3_download(self):
        @fudge.patch('boto3.resource')
        def actual_test(mock_boto_resource):
            download_result = self.some_random_shit('result')
            file_obj = StringIO(download_result)
            fake_s3_object = fudge.Fake().provides('get').returns({'Body': file_obj})
            fake_s3 = fudge.Fake().provides('Object').with_args(self.bucket_name, self.object_name_1).returns(fake_s3_object)
            mock_boto_resource.expects_call().with_args('s3', config=arg.any()).returns(fake_s3)
            result = Downloader.download_bucket(self.s3_bucket_name, self.object_name_1)
            self.assertEqual(result, download_result)

        self._wrap_local_s3_auth(actual_test)

    @httpretty.activate
    def test_s3_download_moniker_in_object_name(self):
        @fudge.patch('boto3.resource')
        def actual_test(mock_boto_resource):
            download_result = self.some_random_shit('result')
            file_obj = StringIO(download_result)
            fake_s3_object = fudge.Fake().provides('get').returns({'Body': file_obj})
            fake_s3 = fudge.Fake().provides('Object').with_args(self.bucket_name, self.object_name_1).returns(fake_s3_object)
            mock_boto_resource.expects_call().with_args('s3', config=arg.any()).returns(fake_s3)
            result = Downloader.download_bucket(None, self.s3_object_name_1)
            self.assertEqual(result, download_result)

        self._wrap_local_s3_auth(actual_test)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    def test_azure_download(self, mock_get_blob_to_bytes):
        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_account=storage_account, storage_key=storage_key)

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        content_data = self.some_random_shit('content')
        content_blob = fudge.Fake().has_attr(content=content_data)

        mock_get_blob_to_bytes.expects_call().with_args(bucket_name, object_name).returns(content_blob)

        self.assertEqual(_az_download(bucket_name, object_name, azure_config=fake_azure_config), content_data)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    @fudge.patch('time.sleep')
    def test_azure_download_raises_AzureMissingResourceHttpError(self, mock_get_blob_to_bytes, mock_sleep):
        from azure.common import AzureMissingResourceHttpError

        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_account=storage_account, storage_key=storage_key)

        bucket_name = self.some_random_shit('bucket_name')
        object_name = self.some_random_shit('object_name')

        message = self.some_random_shit('message')
        status_code = self.some_random_shit_number_int63()

        mock_get_blob_to_bytes.expects_call().with_args(bucket_name, object_name).raises(AzureMissingResourceHttpError(message, status_code))
        mock_sleep.expects_call().times_called(9)

        with self.assertRaises(AzureContainerNotFound):
            _az_download(bucket_name, object_name, azure_config=fake_azure_config)

    @httpretty.activate
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    def test_azure_download_with_full_bucket_name(self, mock_get_blob_to_bytes):
        storage_account = self.some_random_shit('storage_account')
        storage_key = self.some_random_shit('storage_key')
        fake_azure_config = fudge.Fake().has_attr(storage_key=storage_key)

        bucket_name = self.some_random_shit('bucket_name')

        full_bucket_name = '%s.%s' % (storage_account, bucket_name)
        object_name = self.some_random_shit('object_name')

        content_data = self.some_random_shit('content')
        content_blob = fudge.Fake().has_attr(content=content_data)

        mock_get_blob_to_bytes.expects_call().with_args(bucket_name, object_name).returns(content_blob)

        self.assertEqual(_az_download(full_bucket_name, object_name, azure_config=fake_azure_config), content_data)

    @httpretty.activate
    @fudge.patch('msrestazure.azure_active_directory.MSIAuthentication.__init__')
    @fudge.patch('missinglink.legit.azure_config.create_storage_client')
    @fudge.patch('azure.storage.blob.BlockBlobService.get_blob_to_bytes')
    def test_azure_download_with_full_bucket_name_under_msi(self, mock__msi_init, mock_create_storage_client, mock_get_blob_to_bytes):
        from msrestazure.azure_active_directory import MSIAuthentication

        storage_account1 = self.some_random_shit('storage_account1')
        storage_account2 = self.some_random_shit('storage_account2')

        access_key = self.some_random_shit('access_key')
        fake_azure_config = fudge.Fake().has_attr(storage_key=None).provides('set_storage_key_env_var').with_args(access_key).times_called(1)

        bucket_name = self.some_random_shit('bucket_name')

        full_bucket_name = '%s.%s' % (storage_account2, bucket_name)
        object_name = self.some_random_shit('object_name')

        content_data = self.some_random_shit('content')
        content_blob = fudge.Fake().has_attr(content=content_data)

        mock_get_blob_to_bytes.expects_call().with_args(bucket_name, object_name).returns(content_blob)

        subscription_id = self.some_random_shit('subscription_id')
        ml_instance_role = self.some_random_shit('/subscriptions/%s/' % subscription_id)

        mock__msi_init.expects_call().with_args(msi_res_id=ml_instance_role)

        resource_group1 = self.some_random_shit('resource_group1')
        resource_group_id1 = self.some_random_shit('resourceGroups/%s/' % resource_group1)
        fake_item1 = fudge.Fake().has_attr(id=resource_group_id1, name=storage_account1)

        resource_group2 = self.some_random_shit('resource_group1')
        resource_group_id2 = self.some_random_shit('resourceGroups/%s/' % resource_group2)
        fake_item2 = fudge.Fake().has_attr(id=resource_group_id2, name=storage_account2)
        fake_keys = fudge.Fake().has_attr(keys=[fudge.Fake().has_attr(value=access_key)])

        fake_storage_accounts = fudge.Fake().provides('list').returns([fake_item1, fake_item2]).provides('list_keys').with_args(resource_group2, storage_account2).returns(fake_keys)

        fake_storage_client = fudge.Fake().has_attr(storage_accounts=fake_storage_accounts)
        mock_create_storage_client.expects_call().with_args(arg.isinstance(MSIAuthentication), subscription_id).returns(fake_storage_client)

        os.environ['ML_INSTANCE_ROLE'] = ml_instance_role
        try:
            self.assertEqual(_az_download(full_bucket_name, object_name, azure_config=fake_azure_config), content_data)
        finally:
            del os.environ['ML_INSTANCE_ROLE']

    @httpretty.activate
    @fudge.patch('requests.get')
    def test_download_using_secure_url(self, mock_requests_get):
        singed_url = self.some_random_shit('singed_url')
        content = self.some_random_shit('content')
        fake_response = fudge.Fake().provides('raise_for_status').has_attr(content=content)
        mock_requests_get.expects_call().with_args(singed_url).returns(fake_response)

        result = Downloader.download_http(singed_url)
        self.assertEqual(result, content)

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Blob.download_as_string')
    def test_download_under_gae(self, mock_download_as_string):
        download_result = self.some_random_shit('result')
        mock_download_as_string.expects_call().with_args().returns(download_result)

        access_token = self.some_random_shit('access_token')
        project_id = self.some_random_shit('project_id')
        ttl = 3600
        app_engine.app_identity = fudge.Fake().provides('get_access_token').returns((access_token, ttl)).provides('get_application_id').returns(project_id)
        credentials = GCPServices.gcp_default_credentials(scopes=['read-only'])
        try:
            result = GCSDownloadDirectDownload(credentials).download(self.bucket_name, self.object_name_1)
            self.assertEqual(result, download_result)
        finally:
            app_engine.app_identity = None

    @httpretty.activate
    @fudge.patch('google.cloud.storage.Bucket.list_blobs')
    @fudge.patch('google.cloud.storage.Bucket.delete_blob')
    def test_delete_all(self, mock_list_blobs, mock_delete_blob):
        def actual_test():
            volume_id = self.some_random_shit_number_int63()

            fake_blob1 = fudge.Fake().has_attr(name='1')
            mock_list_blobs.expects_call().with_args(prefix=str(volume_id)).returns([fake_blob1])
            mock_delete_blob.expects_call().with_args('1')

            bucket_name = self.some_random_shit('bucket_name')
            max_files = 1000
            do_delete_all(bucket_name, volume_id, max_files)

        self._wrap_gcs_local_auth_files(actual_test)
