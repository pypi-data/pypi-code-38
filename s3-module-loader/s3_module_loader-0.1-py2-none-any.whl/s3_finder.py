from importlib.abc import MetaPathFinder
import boto3
from .s3_loader import S3Loader

s3 = boto3.client('s3')


class S3Finder(MetaPathFinder):
    """Module finder that locates python modules in s3"""
    def __init__(self, bucket):
        self.bucket = bucket
        self.loaders = {}
        self._keys = None

    @property
    def keys(self):
        if self._keys is None:
            results = s3.list_objects_v2(Bucket=self.bucket)
            self._keys = [k['Key'] for k in results['Contents']]
        return self._keys

    def is_s3_module(self, fullname):
        parts = fullname.split('.')
        if len(parts) == 1:
            path = parts[0]
        else:
            path = '/'.join(parts)
        for k in self.keys:
            if k.startswith(path):
                return True
        return False

    def find_module(self, fullname, path=None):
        if not self.is_s3_module(fullname):
            # print(f"This doesn't seem to be a package in s3: {fullname}")
            raise ImportError

        print(f'S3Finder::find_module {fullname} {path}')
        key = fullname
        if key not in self.loaders:
            self.loaders[key] = S3Loader(path, self.bucket)
        return self.loaders[key]

