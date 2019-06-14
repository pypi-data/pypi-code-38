from __future__ import (absolute_import, division, print_function, unicode_literals)

import fnmatch
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from os.path import expanduser

from .klass_operator import Operator
from .klass_str import Str


class Path(object):
    @classmethod
    def join(cls, *args):
        args = Operator.flat(args)
        return os.path.join(*args)

    @classmethod
    @contextmanager
    def chdir(cls, path):
        try:
            origin = os.getcwd()
            os.chdir(path)
            yield
        except Exception as e:
            raise e
        finally:
            os.chdir(origin)

    @classmethod
    @contextmanager
    def tempdir(cls):
        tmpdir = tempfile.mkdtemp()
        try:
            yield tmpdir
        finally:
            shutil.rmtree(tmpdir)

    @classmethod
    @contextmanager
    def tempfile(cls, **kwargs):
        f = tempfile.NamedTemporaryFile(delete=False, **kwargs)
        try:
            yield f
        finally:
            if os.path.isfile(f.name):
                os.remove(f.name)

    @classmethod
    def subpaths(self, path):
        elements = []
        sep = os.path.sep if path.startswith(os.path.sep) else ''
        res = [x for x in path.split(os.path.sep) if x]
        res.reverse()
        while res:
            item = res.pop()
            if elements:
                elements.append(os.path.join(sep, elements[-1], item))
            else:
                elements = [os.path.join(sep, item)]
        return elements if not os.path.isfile(path) else elements[:-1]

    @classmethod
    def create_file(cls, path, content, eof=0, mode='wb+'):
        mode_read = mode.replace('+', '').replace('w', 'r')

        def _erase_data(_path, _content):
            with open(_path, mode) as f:
                f.write(_content)

        if eof:
            content += '\n' * eof
        if not os.path.isfile(path):
            ddir = os.path.dirname(path)
            cls.create_dir(ddir)
            _erase_data(path, content)
        else:
            with open(path, mode_read) as f:
                c = f.read()
            if c != content:
                _erase_data(path, content)

    @classmethod
    def write(cls, path, content, mode='wb+'):
        cls.touch(path)
        with open(path, mode) as f:
            return f.write(content)

    @classmethod
    def read(cls, path, mode='rb'):
        with open(path, mode) as f:
            return f.read()

    @classmethod
    def home(cls):
        return expanduser("~")

    @classmethod
    def touch(cls, *path):
        path = os.path.join(*path)
        cls.create_dir(os.path.dirname(path))
        if not os.path.isfile(path):
            open(path, 'a').close()
        return path

    @classmethod
    def create_dir(cls, path):
        if path:
            os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def create_parent_dir(cls, path):
        if path:
            path = cls.create_dir(os.path.dirname(path))
        return path

    @classmethod
    def clean_dir(cls, path):
        if os.path.exists(path):
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                elif os.path.isfile(full_path):
                    os.remove(full_path)

    @classmethod
    def remove(cls, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)

    @classmethod
    def delete_dir(cls, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    @classmethod
    def clean_empty_dirs(cls, path):
        if os.path.isfile(path):
            path = os.path.dirname(path)
        dirs_to_remove = []
        while True:
            for root, dirnames, filenames in os.walk(path):
                if not dirnames and not filenames:
                    dirs_to_remove.append(root)
            if not dirs_to_remove:
                break
            for dir_to_remove in dirs_to_remove:
                cls.delete_dir(dir_to_remove)
            dirs_to_remove = []

    @classmethod
    def size_str(cls, path, unit='mb'):
        size, u = cls.size(path, unit=unit)
        return '{} {}'.format(size, u)

    @classmethod
    def size(cls, path, unit='mb'):
        total_size = 0
        if os.path.isfile(path):
            total_size = os.path.getsize(path)
        else:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp) if os.path.isfile(fp) else 0
        if unit == 'mb':
            return round(total_size / (1024. * 1024.), 2), 'MB'
        else:
            return round(total_size, 2), 'B'

    @classmethod
    def find_files(cls, expr, path=os.getcwd()):
        if os.path.isfile(path):
            if fnmatch.filter([path], expr):
                return [path]
            else:
                return []
        with cls.chdir(path):
            matches = set()
            for root, dirnames, filenames in os.walk(path):
                for e in Str(expr).case_combinations():
                    for filename in fnmatch.filter(filenames, e):
                        matches.add(os.path.join(root, filename))
            return list(matches)

    @classmethod
    def find_file_path(cls, path, home=False, raise_if_not_found=False):
        full_path = path
        if not os.path.isfile(path):
            if home:
                if os.path.isfile(home):
                    home = os.path.dirname(home)
                full_path = os.path.join(home, path)
        if raise_if_not_found and not os.path.isfile(full_path):
            raise FileNotFoundError('the path [%s] is not a file found' % full_path)
        return full_path

    @classmethod
    def find_dir_path(cls, path, home=False, raise_if_not_found=False):
        full_path = path
        if not os.path.isfile(full_path):
            full_path = os.path.dirname(full_path)
        if not os.path.isdir(full_path):
            if home:
                if os.path.isfile(home):
                    home = os.path.dirname(home)
                full_path = os.path.join(home, path)
        if raise_if_not_found and not os.path.isdir(full_path):
            raise NotADirectoryError('the path [%s] is not a directory' % full_path)
        return full_path

    @classmethod
    def grep(cls, expressions, files, comment=False):
        if not isinstance(expressions, list):
            expressions = [expressions]
        matches = {}
        for file in files:
            with open(file) as f:
                for i, line in enumerate(f.readlines(), start=1):
                    for expr in expressions:
                        pattern = re.compile(expr)
                        if expr in line or pattern.search(line):
                            if comment:
                                pattern = re.compile(comment)
                                if pattern.search(line.strip()):
                                    continue
                            matches.setdefault(file, {})
                            matches[file].setdefault(expr, [])
                            matches[file][expr].append(i)
        return matches
