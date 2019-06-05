import boto3
import os
import errno

from wed.path import DatafilePath


def mkdirs(path):
    """
    Build the directory if it does not exist yet
    """
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno != errno.EEXIST or not os.path.isdir(path):
            raise

def download(path: DatafilePath):
    """
    Download the Datafile to the cache directory
    """
    s3 = boto3.client('s3')
    mkdirs(os.path.dirname(path.local_path))
    s3.download_file(path.bucket, path.prefix, path.local_path)
