'''
This module contains functions to create, access, modify, and delete blobs in GCS.
'''

import os
import pickle
from contextlib import contextmanager

from google.cloud import storage

from .config import CONFIG


def download(bucket_name: str, blob_name: str, file_path=None):
    '''
    This function fetches a blob from GCS and stores it to a local file.
    If no location is given, a file with the same name as the blob will be written to
    the cache directory specified in `CONFIG['cachedir']`.

    :param str bucket_name: the name of the bucket the blob is located in.

    :param str blob_name: the name of the actual blob.

    :param str file_path: the location to write the file contents to (optional).

    :return: a tuple containing the path the file and the corresponding metadata from `blob.metadata`.

    :rtype: tuple(str, dict)
    '''
    if file_path is None:
        file_path = os.path.abspath(f'{CONFIG["cachedir"]}/{blob_name}')

    with get_handle(bucket_name, blob_name) as blob:
        blob.download_to_filename(file_path)
        return file_path, blob.metadata


def load(bucket_name: str, blob_name: str, keep_file: bool = True):
    '''
    This function fetches a blob from GCS and loads it using :mod:`pickle`.

    :see: :func:`~gcshelpers.storage.download`.

    :param str bucket_name: the name of the bucket the blob is located in.

    :param str blob_name: the name of the actual blob.

    :param bool keep_file: whether or not the local intermediate should be kept or deleted after successful upload.

    :return: a tuple containing the unpickled object and the corresponding metadata from `blob.metadata`.

    :rtype: tuple(object, dict)
    '''
    file_path = os.path.abspath(f'{CONFIG["cachedir"]}/{blob_name}')
    file_path, metadata = download(bucket_name, blob_name, file_path=file_path)

    with open(file_path, 'rb') as file_handle:
        obj = pickle.load(file_handle)

        if not keep_file:
            os.remove(file_path)

        return obj, metadata


def upload(bucket_name: str, blob_name: str, file_path: str):
    '''
    Uploads a given file to GCS.

    :param str bucket_name: the name of the bucket the blob is located in.

    :param str blob_name: the name of the target blob.

    :param str file_path: the path to the local file.
    '''
    with get_handle(bucket_name, blob_name) as blob:
        blob.upload_from_filename(file_path)


def store(bucket_name: str, blob_name: str, obj: object, metadata: dict = None, keep_file: bool = False):
    '''
    Pickles a given object and stores it to a blob in GCS. Also sets the metadata of the blob object if any is given.

    :param str bucket_name: the name of the bucket the blob is located in.

    :param str blob_name: the name of the target blob.

    :param object obj: the object that should be stored.

    :param dict metadata: the metadata to be associated with the object.

    :param bool keep_file: whether or not to keep the local intermediate file.
    '''

    file_path = os.path.abspath(f'{CONFIG["cachedir"]}/{blob_name}')

    with open(file_path, 'rb') as file_handle:
        pickle.dump(obj, file_handle)

    upload(bucket_name, blob_name, file_path)
    set_metadata(bucket_name, blob_name, metadata)

    if not keep_file:
        os.remove(file_path)


def rename(bucket_name: str, blob_name: str, new_name: str):
    '''
    Renames a given blob instance.

    :param str bucket_name: the name of the bucket the blob is located in.

    :param str blob_name: the name of the actual blob.

    :param str new_name: the new filename of the blob.
    '''
    with get_handle(bucket_name, blob_name) as blob:
        blob.bucket.rename_blob(blob, new_name)


def set_metadata(bucket_name: str, blob_name: str, metadata: dict):
    '''
    Updates the metadata of a specific blob in GCS.
    See the ``notebooks/blob_metadata_control.ipynb`` for metadata related examples.

    :param str bucket_name: the name of the bucket the blob is located in.
    :param str blob_name: the name of the actual blob.
    '''
    with get_handle(bucket_name, blob_name) as blob:
        blob.metadata = metadata
        blob.update()


def get_metadata(bucket_name: str, blob_name: str):
    '''
    Gets the metadata of a specific blob in GCS.
    See the `notebooks/blob_metadata_control.ipynb` for metadata related examples.

    :param str bucket_name: the name of the bucket the blob is located in.
    :param str blob_name: the name of the actual blob.
    '''
    with get_handle(bucket_name, blob_name) as blob:
        return blob.metadata


def del_metadata(bucket_name: str, blob_name: str):
    '''
    Updates the metadata of a specific blob in GCS.
    See the `notebooks/blob_metadata_control.ipynb` for metadata related examples.

    :param str bucket_name: the name of the bucket the blob is located in.
    :param str blob_name: the name of the actual blob.
    '''
    with get_handle(bucket_name, blob_name) as blob:
        blob.metadata = None
        blob.update()


@contextmanager
def get_handle(bucket_name: str, blob_name: str):
    '''
    Creates a blob object handle that can be used to access the blob and its metadata.

    :param str bucket_name: the name of the bucket the blob is located in.
    :param str blob_name: the name of the actual blob.
    '''
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    yield blob
