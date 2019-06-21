import os
import shutil
import tempfile
from urllib.parse import urlparse

import boto3
import fs

from .abstract_walker import AbstractWalker, FileInfo


class S3Walker(AbstractWalker):
    """Walker that is implemented in terms of S3"""
    """By default, use '/' for S3 list objects path delimiter"""
    def __init__(self, fs_url, ignore_dot_files=True, follow_symlinks=False, filter=None, exclude=None,
                 filter_dirs=None, exclude_dirs=None):
        """Initialize the abstract walker

        Args:
            fs_url (str): The starting directory for walking
            ignore_dot_files (bool): Whether or not to ignore files starting with '.'
            follow_symlinks(bool): Whether or not to follow symlinks
            filter (list): An optional list of filename patterns to INCLUDE
            exclude (list): An optional list of filename patterns to EXCLUDE
            filter_dirs (list): An optional list of directories to INCLUDE
            exclude_dirs (list): An optional list of patterns of directories to EXCLUDE
        """
        schema, bucket, path, *_ = urlparse(fs_url)

        sanitized_path = '' if path == '/' else path.rstrip('/')

        super(S3Walker, self).__init__(sanitized_path, ignore_dot_files=ignore_dot_files,
                                       follow_symlinks=follow_symlinks, filter=filter, exclude=exclude,
                                       filter_dirs=filter_dirs, exclude_dirs=exclude_dirs)
        self.bucket = bucket
        self.client = boto3.client('s3')
        self.fs_url = fs_url
        self.tmp_dir_path = tempfile.mkdtemp()

    def get_fs_url(self):
        return self.fs_url

    def close(self):
        if self.tmp_dir_path is not None:
            shutil.rmtree(self.tmp_dir_path)
            self.tmp_dir_path = None

    def open(self, path, mode='rb', **kwargs):
        file_path = os.path.join(self.tmp_dir_path, self.root.lstrip('/'), path.lstrip('/'))

        if not os.path.isfile(file_path):
            prefix_dir = '' if path.count('/') == 1 else path.rsplit('/', 1)[0]
            file_dir = os.path.join(self.tmp_dir_path, self.root.lstrip('/'), prefix_dir.lstrip('/'))
            os.makedirs(file_dir, exist_ok=True)

            prefix_path = (self.root + path).lstrip('/')

            self.client.download_file(self.bucket, prefix_path, file_path)

        try:
            return open(file_path, mode, **kwargs)
        except fs.errors.ResourceNotFound:
            raise FileNotFoundError('File {} not found'.format(path))

    def _listdir(self, path):
        if path == '/' or path == '':
            prefix_path = ''
        elif path.endswith('/'):
            prefix_path = path.lstrip('/')
        else:
            prefix_path = path.lstrip('/') + '/'

        paginator = self.client.get_paginator('list_objects')
        page_iterator = paginator.paginate(Bucket=self.bucket, Prefix=prefix_path, Delimiter='/')
        for page in page_iterator:
            if 'CommonPrefixes' in page:
                common_prefixes = page['CommonPrefixes']
                for common_prefix in common_prefixes:
                    prefix = common_prefix['Prefix'].rstrip('/')
                    dir_name = prefix if prefix_path == '' else prefix.split(prefix_path)[1]
                    yield FileInfo(dir_name, True)

            if 'Contents' in page:
                contents = page['Contents']
                for content in contents:
                    file_name = content['Key'] if prefix_path == '' else content['Key'].split(prefix_path)[1]
                    last_modified = content['LastModified']
                    size = content['Size']
                    yield FileInfo(file_name, False, modified=last_modified, size=size)
