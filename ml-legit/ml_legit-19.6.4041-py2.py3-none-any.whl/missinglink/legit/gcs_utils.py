# -*- coding: utf-8 -*-
import errno
import logging
import os
import sys
import threading
import time

import requests
import six
from requests.exceptions import MissingSchema, InvalidSchema

from missinglink.legit.azure_config import get_access_key_using_msi
from .gcp_services import GCPServices, GooglePackagesMissing, GoogleAuthError
from missinglink.core.exceptions import NonRetryException, NotFound, AccessDenied
from .path_utils import remove_moniker, get_moniker


class closing_with_condition(object):
    def __init__(self, thing, should_close):
        self.thing = thing
        self.should_close = should_close

    def __enter__(self):
        return self.thing

    def __exit__(self, *exc_info):
        if self.should_close:
            self.thing.close()


class CloudService(object):
    RETRYABLE_ERRORS = (IOError, )
    DEFAULT_MIMETYPE = 'application/octet-stream'
    NUM_RETRIES = 5


class GCSService(CloudService):
    def __init__(self, credentials=None):
        self._credentials = credentials


class GCSDownloadDirectDownload(GCSService):
    def __init__(self, credentials=None):
        super(GCSDownloadDirectDownload, self).__init__(credentials)

    def download(self, bucket_name, object_name):
        import google.auth.exceptions as google_auth_exceptions

        gcs = GCPServices.gcs_service(self._credentials)

        bucket_name = remove_moniker(bucket_name)

        blob = gcs.bucket(bucket_name).blob(object_name)
        try:
            return blob.download_as_string()
        except google_auth_exceptions.GoogleAuthError:
            raise GoogleAuthError()


def __convert_s3_client_error(bucket_name, key, ex):
    if ex.response.get('Error', {}).get('Code') == 'RequestTimeout':
        exc_info = sys.exc_info()
        six.reraise(*exc_info)

    default_resource_name = 's3://%s/%s' % (bucket_name, key)
    resource_name = ex.response.get('Error', {}).get('Key', default_resource_name)
    code = ex.response.get('Error', {}).get('Code')

    if code == 'AccessDenied':
        raise AccessDenied('Access Denied %s' % (resource_name, ))

    if code == 'NoSuchKey':
        raise NotFound('Object not found %s' % (resource_name, ))

    raise NonRetryException('%s (%s)' % (ex, resource_name))


class AzureContainerNotFound(NonRetryException):
    max_attempts = 10


def _wrap_azure_call(callback, bucket_name, key, *args, **kwargs):
    from azure.common import AzureMissingResourceHttpError, AzureHttpError, AzureException

    try:
        return callback(*args, **kwargs)
    except AzureMissingResourceHttpError:
        six.raise_from(AzureContainerNotFound('container %s not found' % bucket_name), None)
    except AzureHttpError as ex:
        if ex.status_code == 404:
            six.raise_from(NotFound('object Not Found %s' % key), None)

        if ex.status_code == 403:
            six.raise_from(AccessDenied(key), None)

        six.raise_from(NonRetryException('Download failed %s %s' % (ex, key)), None)


_s3_thread_local_objects = threading.local()
_s3_thread_global_objects = {}
_s3_thread_global_objects_lock = threading.Lock()


def _clear_cached_objects():
    global _s3_thread_local_objects
    global _s3_thread_global_objects

    with _s3_thread_global_objects_lock:
        _s3_thread_local_objects = threading.local()
        _s3_thread_global_objects = {}


def __get_cached_object(object_name, object_creator):
    obj = getattr(_s3_thread_local_objects, object_name, None)

    if obj is None:
        with _s3_thread_global_objects_lock:
            obj = _s3_thread_global_objects.get(object_name)
            if obj is None:
                obj = object_creator()
                _s3_thread_global_objects[object_name] = obj
                setattr(_s3_thread_local_objects, object_name, obj)

    return obj


def _get_boto_local_resource(name):
    object_name = '_boto_resource_%s' % name

    def create_boto_resource():
        import boto3
        import botocore

        max_pool_connections = os.environ.get('ML_BOTO_MAX_POOL_CONNECTIONS', 500)

        return boto3.resource(name, config=botocore.client.Config(max_pool_connections=max_pool_connections))

    return __get_cached_object(object_name, create_boto_resource)


def _get_boto_local_client(name):
    object_name = '_boto_client_%s' % name

    def create_boto_client():
        import boto3

        return boto3.client(name)

    return __get_cached_object(object_name, create_boto_client)


def _wrap_s3_call(callback, bucket_name, key, s3_client=None):
    from botocore.exceptions import ClientError, BotoCoreError

    bucket_name = remove_moniker(bucket_name)

    s3_client = s3_client or _get_boto_local_client('s3')

    try:
        return callback(s3_client, bucket_name, key)
    except s3_client.exceptions.NoSuchBucket:
        raise NotFound('No such S3 Bucket %s' % bucket_name)
    except BotoCoreError as ex:
        raise NonRetryException('%s (s3://%s/%s)' % (ex, bucket_name, key))
    except ClientError as ex:
        __convert_s3_client_error(bucket_name, key, ex)


def _open_file_with_exp(full_path_to_data):
    while True:
        try:
            return open(full_path_to_data, 'rb')
        except (IOError, OSError) as ex:
            if ex.errno == errno.EMFILE:  # too many open files
                time.sleep(1)
                continue

            raise NonRetryException('failed to open %s\n%s' % (full_path_to_data, ex))


def _handle_file_object(full_path_to_data, callback_with_file_obj):
    if hasattr(full_path_to_data, 'read'):
        full_path_to_data.seek(0)
        should_close = False
        file_obj = full_path_to_data
    else:
        should_close = True
        file_obj = _open_file_with_exp(full_path_to_data)

    try:
        return callback_with_file_obj(file_obj)
    finally:
        if should_close:
            file_obj.close()


class S3DownloadDirectDownload(CloudService):
    @classmethod
    def download(cls, bucket_name, object_name):
        def s3_call(_s3_client, s3_bucket_name, s3_object_name):
            s3_resource = _get_boto_local_resource('s3')

            obj = s3_resource.Object(s3_bucket_name, s3_object_name)
            return obj.get()['Body'].read()

        return _wrap_s3_call(s3_call, bucket_name, object_name)


class GCSUploadDirect(GCSService):
    def __init__(self, credentials):
        super(GCSUploadDirect, self).__init__(credentials)

    def upload(self, bucket_name, object_name, full_path_to_data, headers):
        logging.info('gcs upload (direct) bucket: %s %s', bucket_name, object_name)

        try:
            import google.api_core.exceptions as google_exceptions
        except ImportError:
            raise GooglePackagesMissing()

        bucket_name = remove_moniker(bucket_name)

        gcs = GCPServices.gcs_service(self._credentials)

        blob = gcs.bucket(bucket_name).blob(object_name)

        content_type = (headers or {}).get('Content-Type')

        def handle_upload(file_obj):
            blob.upload_from_file(file_obj, content_type)

        try:
            _handle_file_object(full_path_to_data, handle_upload)
        except google_exceptions.NotFound:
            raise NotFound('bucket %s not found' % bucket_name)
        except google_exceptions.PermissionDenied:
            raise AccessDenied('access denied to bucket %s' % bucket_name)


class S3UploadDirect(CloudService):
    def __init__(self, s3_client):
        self._s3_client = s3_client

    # noinspection PyUnusedLocal
    def upload(self, bucket_name, object_name, full_path_to_data, headers):
        logging.info('s3 upload %s %s %s %s', bucket_name, object_name, full_path_to_data, headers)

        def s3_call(s3_client, s3_bucket_name, s3_object_name):
            def upload_file_objkect(file_obj):
                s3_client.upload_fileobj(file_obj, s3_bucket_name, s3_object_name)

            _handle_file_object(full_path_to_data, upload_file_objkect)

            logging.info('s3 uploaded %s %s', bucket_name, object_name)

        return _wrap_s3_call(s3_call, bucket_name, object_name, s3_client=self._s3_client)

    def copy(self, src, dest):
        logging.info('s3 copy %s => %s', src, dest)

        bucket_name, key = dest.split('/', 1)

        def s3_call(s3_client, s3_bucket_name, s3_key):
            s3_client.copy_object(Bucket=s3_bucket_name, CopySource=src, Key=s3_key)
            logging.info('s3 copied %s => %s', src, dest)

        logging.info('s3 copy %s => %s', src, dest)

        return _wrap_s3_call(s3_call, bucket_name, key, s3_client=self._s3_client)


class FileWithCallback(object):
    def __init__(self, file_obj, callback):
        file_obj.seek(0, 2)
        self._total = file_obj.tell()
        file_obj.seek(0)

        self._callback = callback
        self._file_obj = file_obj

    def __len__(self):
        return self._total

    def read(self, size):
        data = self._file_obj.read(size)
        if not six.PY2 and isinstance(data, six.string_types):
            data = data.encode()

        if six.PY3 and isinstance(data, six.string_types):
            data = data.encode()

        if self._callback is not None:
            self._callback(len(data))

        return data


class HttpUploader(object):
    @classmethod
    def _check_head_url(cls, session, head_url):
        if not head_url:
            return

        logging.debug('try head url')
        resp = session.head(head_url)

        logging.debug('try head resp %s', resp)

        if resp.status_code in (204, 404):
            logging.debug('file not found, uploading')
            resp = None

        return resp

    @classmethod
    def put_file(cls, session, put_url, headers, progress_callback):
        def wrap(file_obj):
            file_obj_with_callback = FileWithCallback(file_obj, progress_callback)

            logging.debug('put url')
            put_resp = session.put(put_url, data=file_obj_with_callback, headers=headers)
            logging.debug('put url done %s', put_resp)

            return put_resp

        return wrap

    @classmethod
    def upload(cls, session, put_url, head_url, full_path_to_data, headers, progress_callback=None):
        logging.info('gcs upload head: "%s" put: "%s"', head_url, put_url)

        try:
            resp = cls._check_head_url(session, head_url)

            if resp is None:
                resp = _handle_file_object(full_path_to_data, cls.put_file(session, put_url, headers, progress_callback))

            if resp.status_code in (401, 403):
                raise NonRetryException()

            resp.raise_for_status()
        except (MissingSchema, InvalidSchema, MissingSchema):
            logging.exception('Invalid request')
            raise NonRetryException('Invalid request')


class GCSDeleteAll(GCSService):
    def __init__(self, credentials):
        super(GCSDeleteAll, self).__init__(credentials)

    def delete_all(self, bucket_name, volume_id, max_files=None):
        try:
            import google.api_core.exceptions as google_exceptions
        except ImportError:
            raise GooglePackagesMissing()

        logging.info('delete all at %s/%s', bucket_name, volume_id)
        gcs = GCPServices.gcs_service(self._credentials)

        try:
            list_iter = gcs.bucket(bucket_name).list_blobs(prefix=str(volume_id))
        except google_exceptions.NotFound:
            logging.warning('bucket %s was not found', bucket_name)
            return

        total_deleted = 0
        for blob in list_iter:
            try:
                gcs.bucket(bucket_name).delete_blob(blob.name)
            except google_exceptions.NotFound:
                pass

            total_deleted += 1

            if max_files is not None and max_files == total_deleted:
                break

        logging .info('total deleted %s', total_deleted)

        return total_deleted


s3_moniker = 's3://'
gcs_moniker = 'gs://'
azure_moniker = 'az://'


class _DefaultRetry(object):
    @classmethod
    def _is_non_retry_exception(cls, exception):
        return isinstance(exception, (ImportError, AttributeError, TypeError, AssertionError, ValueError, NonRetryException))

    @classmethod
    def _retry_if_retry_possible_error(cls, exception):
        logging.debug('got retry exception (upload/download) (%s, %s)', exception, type(exception))

        return not cls._is_non_retry_exception(exception)

    @classmethod
    def _check_max_attempt(cls, attempt):
        exception = attempt.value[1]

        max_attempts = getattr(type(exception), 'max_attempts', None)

        if max_attempts is not None:
            logging.debug('got retry exception (upload/download) (%s, %s) (attempt %s/%s)', exception, type(exception), attempt.attempt_number, max_attempts)
            return attempt.attempt_number < max_attempts

    @classmethod
    def _should_reject(cls, attempt):
        reject = False
        if attempt.has_exception:
            reject = cls._retry_if_retry_possible_error(attempt.value[1])

            if not reject:
                max_attempt_reject = cls._check_max_attempt(attempt)

                if max_attempt_reject is not None:
                    return max_attempt_reject

        return reject

    @classmethod
    def create(cls):
        from retrying import Retrying

        retrying = Retrying(
            retry_on_exception=cls._retry_if_retry_possible_error,
            wait_exponential_multiplier=50,
            wait_exponential_max=5000)

        retrying.should_reject = cls._should_reject

        return retrying


def _default_retry():
    def wrap(f):
        @six.wraps(f)
        def wrapped_f(*args, **kwargs):
            retrying = _DefaultRetry.create()
            return retrying.call(f, *args, **kwargs)

        return wrapped_f

    return wrap


@_default_retry()
def _az_upload_or_transfer(bucket_name, object_name, full_path_to_data, headers, azure_config=None):
    from azure.storage.blob import ContentSettings

    bucket_name = remove_moniker(bucket_name)

    def actual_upload(file_obj):
        content_type = headers.pop('Content-Type', None)

        content_settings = ContentSettings(content_type=content_type)

        block_blob_service.create_blob_from_stream(
            actual_bucket_name, object_name, file_obj, metadata=headers, content_settings=content_settings)

    def handle_upload(file_obj):
        _wrap_azure_call(actual_upload, bucket_name, object_name, file_obj)

    block_blob_service, actual_bucket_name = __az_create_blob_service(bucket_name, azure_config)
    _handle_file_object(full_path_to_data, handle_upload)


@_default_retry()
def _s3_upload_or_transfer(bucket_name, object_name, full_path_to_data, headers, s3_client=None):
    bucket_name = remove_moniker(bucket_name)

    if isinstance(full_path_to_data, six.string_types) and full_path_to_data.startswith(s3_moniker):
        full_s3_path = remove_moniker(full_path_to_data)
        object_name_with_bucket = bucket_name + '/' + object_name
        S3UploadDirect(s3_client).copy(full_s3_path, object_name_with_bucket)
        return

    S3UploadDirect(s3_client).upload(bucket_name, object_name, full_path_to_data, headers)


@_default_retry()
def _gs_upload_or_transfer(bucket_name, object_name, full_path_to_data, headers):
    credentials = GCPServices.gcp_default_credentials(scopes=['https://www.googleapis.com/auth/devstorage.read-write'])

    GCSUploadDirect(credentials).upload(bucket_name, object_name, full_path_to_data, headers)


class Uploader(object):
    @classmethod
    @_default_retry()
    def upload_http(cls, put_url, head_url, full_path_to_data, headers, progress_callback=None):
        HttpUploader.upload(requests, put_url, head_url, full_path_to_data, headers, progress_callback)

    @classmethod
    def upload_bucket(cls, bucket_name, object_name, full_path_to_data, headers):
        moniker = get_moniker(bucket_name, gcs_moniker)

        function_name = '_{moniker}_upload_or_transfer'.format(moniker=moniker)
        upload_or_transfer_method = getattr(sys.modules[__name__], function_name)
        upload_or_transfer_method(bucket_name, object_name, full_path_to_data, headers)


@_default_retry()
def _gs_download(bucket_name, object_name, gs_credentials=None):
    try:
        from google.auth.exceptions import DefaultCredentialsError
    except ImportError:
        raise GooglePackagesMissing()

    try:
        credentials = gs_credentials or GCPServices.gcp_default_credentials(scopes=['https://www.googleapis.com/auth/devstorage.read-only'])

        return GCSDownloadDirectDownload(credentials).download(bucket_name, object_name)
    except DefaultCredentialsError as ex:
        logging.info('Failed to get GCP credentials %s', ex)
        raise NonRetryException(ex)


@_default_retry()
def _s3_download(bucket_name, object_name):
    if object_name.startswith(s3_moniker):
        object_name = remove_moniker(object_name)
        bucket_name, object_name = object_name.split('/', 1)

    return S3DownloadDirectDownload().download(bucket_name, object_name)


def __az_create_blob_service(bucket_name, azure_config):
    from azure.storage.blob import BlockBlobService
    from missinglink.legit.azure_config import AzureConfig
    from azure.storage.common import ExponentialRetry
    from azure.common import AzureMissingResourceHttpError

    azure_config = azure_config or AzureConfig()

    bucket_name_parts = bucket_name.split('.')

    if len(bucket_name_parts) == 1:
        storage_account_name = azure_config.storage_account
        actual_bucket_name = bucket_name
    else:
        storage_account_name = bucket_name_parts[0]
        actual_bucket_name = bucket_name_parts[1]

    storage_key = azure_config.storage_key

    if not storage_key:
        storage_key = get_access_key_using_msi(storage_account_name)
        azure_config.set_storage_key_env_var(storage_key)

    blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_key)

    class ExponentialRetryMonitor(ExponentialRetry):
        def retry(self, context):
            if isinstance(context.exception, requests.exceptions.ConnectionError):
                raise AzureMissingResourceHttpError(None, 404)

            return super(ExponentialRetryMonitor, self).retry(context)

    blob_service.retry = ExponentialRetryMonitor().retry

    return blob_service, actual_bucket_name


@_default_retry()
def _az_download(bucket_name, object_name, azure_config=None):
    bucket_name = remove_moniker(bucket_name)

    block_blob_service, storage_account_name = __az_create_blob_service(bucket_name, azure_config)

    def actual_download():
        result = block_blob_service.get_blob_to_bytes(storage_account_name, object_name)

        return result.content

    return _wrap_azure_call(actual_download, bucket_name, object_name)


class Downloader:
    _threadLocal = threading.local()

    @classmethod
    @_default_retry()
    def download_http(cls, download_url):
        import requests

        r = requests.get(download_url)  # allowed to use requests
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            if ex.response.status_code == 404:
                raise NotFound('Url Not Found %s' % download_url)

            raise NonRetryException('Download failed %s %s' % (ex, download_url))

        data = r.content

        logging.debug('downloaded  %s(%s)', download_url, len(data))

        return data

    @classmethod
    def download_bucket(cls, bucket_name, object_name):
        moniker = get_moniker(object_name) or get_moniker(bucket_name, gcs_moniker)

        function_name = '_{moniker}_download'.format(moniker=moniker)
        upload_or_transfer_method = getattr(sys.modules[__name__], function_name)
        return upload_or_transfer_method(bucket_name, object_name)


def do_delete_all(bucket_name, volume_id, max_files):
    credentials = GCPServices.gcp_default_credentials(scopes=['https://www.googleapis.com/auth/devstorage.read_write'])

    return GCSDeleteAll(credentials).delete_all(bucket_name, volume_id, max_files)
