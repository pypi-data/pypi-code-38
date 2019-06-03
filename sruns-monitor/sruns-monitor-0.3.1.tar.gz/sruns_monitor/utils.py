# -*- coding: utf-8 -*-

import os
import psutil
import tarfile
import time

import pdb

import sruns_monitor as srm


def tar(input_dir, tarball_name):
    """
    Creates a tar.gz tarball of the provided directory and returns the tarball's name.
    The tarball's name is the same as the input directory's name, but with a .tar.gz extension.

    Args:
        input_dir: `str`. Path to the directory to tar up.
        tarball_name: `str`. Name of the output tarball.

    Returns:
        `None`.
    """
    with tarfile.open(tarball_name, mode="w:gz") as tb:
        tb.add(name=input_dir, arcname=os.path.basename(input_dir))

def upload_to_gcp(bucket, blob_name, source_file):
    """
    Uploads a local file to GCP storage in the specified bucket.

    Args:
        bucket: `google.cloud.storage.bucket.Bucket` instance, which can be created like so::

            from google.cloud import storage
            storage_client = storage.Client()
            bucket = storage_client.get_bucket("my_bucket_name")

        blob_name: `str`. The name to give the uploaded file in the bucket.
        source_file: `str`. The name of the local file to upload.

    Returns:
        `None`.

    Raises:
        `FileNotFoundError`: source_file was not locally found.
    """
    blob = bucket.blob(blob_name)
    return blob.upload_from_filename(source_file)

def get_process(pid):
    """
    Args:
        pid: `int`. The process ID of a process.

    Returns:
        `psutil.Process`: There is a process that exists in the system process table.
        `None`: There is not a process that exists in the system process table.
    """
    try:
        process = psutil.Process(pid)
        return process
    except psutil.NoSuchProcess:
        return None

def running_too_long(process, limit_seconds=None):
    """
    Indicates whether a process has been running longer than a specified amount of time
    in seconds.

    Args:
       process: `psutil.Process` instance.
       limit_seconds: `int`. Number of seconds. If the process has
           been running longer than this amount of seconds, this function will return True.

    Returns:
        `boolean`.
    """
    if not limit_seconds:
        return False
    created_at = process.create_time() # Seconds since epoch
    process_age = (time.time() - created_at)
    if process_age > limit_seconds:
        return True
    return False
