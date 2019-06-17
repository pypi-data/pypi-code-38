import sys
import imp
from importlib.abc import Loader
import boto3

s3 = boto3.client('s3')

class S3Loader(Loader):
    """Module Loader for python modules in S3"""
    def __init__(self, path=None, bucket=None):
        self.path = path
        self.bucket = bucket
        self._keys = None

    def _get_keys(self):
        if self._keys is None:
            results = s3.list_objects_v2(Bucket=self.bucket)
            self._keys = [k['Key'] for k in results['Contents']]
        return self._keys

    def _get_filename(self, fullname):
        # Make up a fake filename that starts with the path entry
        # so pkgutil.get_data() works correctly.
        return fullname

    # I don't know why this does, but it seems to...for now.
    def is_package(self, fullname):
        # if fullname == self.package_prefix:
        #     return True
        return True

    def is_package_path(self, path):
        matches = [k for k in self._get_keys() if f'{path}.py' == k]
        if len(matches) > 0:
            return False
        return True

    def does_path_exist(self, path):
        for k in self._get_keys():
            if k == path:
                return True
        return False

    def get_source(self, fullname):
        path_parts = fullname.split('.')
        s3_path = '/'.join(path_parts)

        print(f'S3Loader::get_source loading source for {fullname} from {s3_path}')
        obj = None
        if self.is_package_path(s3_path):
            path = f'{s3_path}/__init__.py'
            if self.does_path_exist(path):
                obj = s3.get_object(Bucket=self.bucket, Key=path)
        else:
            path = f'{s3_path}.py'
            if self.does_path_exist(path):
                obj = s3.get_object(Bucket=self.bucket, Key=path)

        if obj:
            source = obj['Body'].read().decode('utf-8')
            return source
        else:
            return None

    def get_code(self, fullname):
        print(f'S3Loader::get_code loading code for {fullname}')
        source = self.get_source(fullname)
        return compile(source, self._get_filename(fullname), 'exec', dont_inherit=True)

    def load_module(self, fullname):
        """import a module in s3 as a module"""

        if fullname in sys.modules:
            return sys.modules[fullname]

        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))

        # Set a few properties required by PEP 302
        mod.__file__ = self._get_filename(fullname)
        mod.__name__ = fullname
        mod.__path__ = self.path
        mod.__loader__ = self
        # PEP-366 specifies that package's set __package__ to
        # their name, and modules have it set to their parent
        # package (if any).
        if self.is_package(fullname):
            mod.__package__ = fullname
        else:
            mod.__package__ = '.'.join(fullname.split('.')[:-1])

        if self.is_package(fullname):
            # Set __path__ for packages
            # so we can find the sub-modules.
            mod.__path__ = [self.path]
        else:
            pass

        source = self.get_source(fullname)
        if source:
            exec(source, mod.__dict__)

        return mod

