"""
Tiny file I/O wrapper for both local and S3 files.
"""
import io
import datetime
import logging
import os

import boto3

name = 'pys3'

def is_s3_path(path):
    return path[0:5] == "s3://"


def split_s3_path(s3_path):
    """
    Split a given s3:// style path into bucket name and file path
    :param s3_path: the s3 url to split
    :return: (None, None) if s3_path is not a correct s3_path, returns the split string otherwise
    """
    if not is_s3_path(s3_path):
        logging.warning("Specified path is not a valid S3 path.")
        return None, None
    s3_path_list = s3_path[5:].split('/')
    file_path = '/'.join(s3_path_list[1:])
    bucket_name = s3_path_list[0]
    return bucket_name, file_path


class PyS3:
    def __init__(self, path, mode='r'):
        self.path = path
        self.bucket_name = ''
        self.s3_file_path = ''
        self.position = 0
        self.modified = False
        if is_s3_path(path):
            # Construct unique identifier from current time
            self.local_path = '/tmp/' + datetime.datetime.now().isoformat() + '_' + path[4:]
            os.makedirs(os.path.dirname(self.local_path))
            self.bucket_name, self.s3_file_path = split_s3_path(path)
            # Download file to local path
            self.s3 = boto3.resource('s3')
            objs = list(self.s3.Bucket(self.bucket_name).objects.filter(Prefix=self.s3_file_path))
            if len(objs) > 0 and objs[0].key == self.s3_file_path:
                self.s3.Bucket(self.bucket_name).download_file(self.s3_file_path, self.local_path)
        else:
            self.local_path = path
        self.fd = open(self.local_path, mode)

    def __repr__(self):
        return "<%s path=%r>" % (type(self).__name__, self.path)

    @property
    def size(self):
        return self.fd.size

    def tell(self):
        return self.fd.tell()

    def write(self, *args, **kwargs):
        self.modified = True
        self.fd.write(*args, **kwargs)

    def writelines(self, *args, **kwargs):
        self.modified = True
        self.fd.writelines(*args, **kwargs)

    def read(self, *args, **kwargs):
        self.fd.read(*args, **kwargs)

    def close(self):
        self.fd.close()
        # If modified, upload file to S3
        if is_s3_path(self.path) and self.modified:
            self.s3.Bucket(self.bucket_name).upload_file(self.local_path, self.s3_file_path)
        # Remove local file
        os.remove(self.local_path)