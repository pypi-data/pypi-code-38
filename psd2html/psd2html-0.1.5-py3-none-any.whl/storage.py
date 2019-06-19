from contextlib import contextmanager
import os


def get_storage(dirname, **kwargs):
    if kwargs.get('type') == 'res':
        return UrlStorage(dirname)
    else:
        return FileSystemStorage(dirname)


class FileSystemStorage:
    def __init__(self, path):
        self.basedir = path
        if not self.basedir:
            self.basedir = '.'

    @staticmethod
    def _ensure_dir(dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    @contextmanager
    def open(self, filename, mode='rb'):
        path = os.path.join(self.basedir, filename)
        if mode.startswith('w'):
            self._ensure_dir(os.path.dirname(path))
        with open(path, mode) as f:
            yield f

    def put(self, filename, value, mode='wb'):
        with self.open(filename, mode=mode) as f:
            f.write(value)

    def url(self, path=''):
        return os.path.abspath(os.path.join(self.basedir, path))


class UrlStorage:
    def __init__(self, res_dir):
        self.res_dir = res_dir
        self.dir()

    @contextmanager
    def put(self, filename, value, mode='wb'):
        path = os.path.join(self.res_dir, filename)
        with open(path, mode=mode) as f:
            f.write(value)

    def dir(self):
        dir_path = self.res_dir
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
