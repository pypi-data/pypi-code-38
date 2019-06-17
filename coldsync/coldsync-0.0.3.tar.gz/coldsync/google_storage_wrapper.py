"""
Implements the base communication via the google-cloud-storage library.
"""

import google as google
from google.cloud import storage


def create_bucket(client, bucket_name, location, storage_class):
    # Set properties on a plain resource object.
    bucket = storage.Bucket(client, name=bucket_name)
    bucket.location = location
    bucket.storage_class = storage_class

    bucket = client.create_bucket(bucket)
    return bucket


def is_bucket_present(client, bucket_name):
    """ Check if a bucket already exists """
    try:
        client.get_bucket(bucket_name)
        return True
    except google.api_core.exceptions.NotFound:
        return False


def upload_file(client, bucket_name, file_name, path_to_blob=None):
    """ Uploads a file to a bucket, if the file is empty no uploads are created"""
    bucket = client.get_bucket(bucket_name)
    if path_to_blob is None:
        path_to_blob = file_name

    blob2 = bucket.blob(path_to_blob)
    blob2.upload_from_filename(filename=file_name)


def download_file(client, bucket_name, path_to_blob, output_file_name):
    """ Downloads a file from a bucket """
    try:
        bucket = client.get_bucket(bucket_name)
        blob = storage.Blob(path_to_blob, bucket)
        with open(output_file_name, 'wb') as file_obj:
            client.download_blob_to_file(blob, file_obj)  # API request.
    except google.api_core.exceptions.NotFound:
        print("Could not find provided file: '%s'" % path_to_blob)


def delete_file(client, bucket_name, path_to_blob):
    """ Removes a stored blob by storage path and returns True if file was deleted, otherwise False. """
    try:
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(path_to_blob)
        blob.delete()
        return True
    except google.api_core.exceptions.NotFound:
        return False


def get_all_files(client, bucket_name):
    """ Returns a list of files in the bucket """
    bucket = client.get_bucket(bucket_name)
    return [x.name for x in bucket.list_blobs()]


def list_all_files(client, bucket_name):
    """ Prints all blobs in the bucket """
    bucket = client.get_bucket(bucket_name)
    for blob in bucket.list_blobs():
        print(blob.name)
