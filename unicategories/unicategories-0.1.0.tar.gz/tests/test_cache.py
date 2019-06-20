
import os
import os.path
import shutil
import sys
import io
import pickle
import contextlib
import tempfile
import warnings
import unittest

import unicategories_tools.cache as cache


class TestCache(unittest.TestCase):
    @contextlib.contextmanager
    def tempsyspath(self):
        # FIXME: use tempfile.TemporaryDirectory on python2 drop
        path = tempfile.mkdtemp()
        sys.path.insert(0, path)
        yield path
        sys.path.remove(path)
        shutil.rmtree(path)

    @contextlib.contextmanager
    def tempdir(self):
        # FIXME: use tempfile.TemporaryDirectory on python2 drop
        path = tempfile.mkdtemp()
        yield path
        shutil.rmtree(path)

    def write_file(self, path, data=b''):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with io.open(path, 'wb') as f:
            f.write(data)

    def write_cache_file(self, path, cache_version=cache.cache_version,
                         cache_format=cache.cache_formats[-1], data={}):
        data = pickle.dumps((cache_version, cache_format, data))
        self.write_file(path, data)

    @contextlib.contextmanager
    def assertWarningText(self, text):
        with warnings.catch_warnings(record=True) as w:
            yield
            messages = [str(warning.message) for warning in w]
            self.assertTrue(
                any(text in m for m in messages) or
                any(text.lower() in m.lower() for m in messages),
                'Unable to find %r in warnings: %r' % (text, messages)
                )

    @contextlib.contextmanager
    def assertNoWarning(self):
        with warnings.catch_warnings(record=True) as w:
            yield
            self.assertFalse(w)

    def test_load_from_package(self):
        with self.tempsyspath() as path:
            self.write_file(os.path.join(path, 'mymodule', '__init__.py'))
            args = ('mymodule', 'db.bin')
            path = os.path.join(path, *args)

            self.write_cache_file(path)
            self.assertEqual(cache.load_from_package(*args), {})

            self.write_cache_file(path, cache_version='0')
            with self.assertWarningText('outdated'):
                self.assertEqual(cache.load_from_package(*args), None)

            self.write_cache_file(path, cache_format='invalid')
            with self.assertWarningText('incompatible'):
                self.assertEqual(cache.load_from_package(*args), None)

            self.write_file(path)
            with self.assertWarningText('incompatible'):
                self.assertEqual(cache.load_from_package(*args), None)

            os.remove(path)
            with self.assertNoWarning():
                self.assertEqual(cache.load_from_package(*args), None)

    def test_load_from_cache(self):
        with self.tempdir() as path:
            path = os.path.join(path, 'db.bin')
            with self.assertNoWarning():
                self.write_cache_file(path)
                self.assertEqual(cache.load_from_cache(path), {})
                self.write_cache_file(path, cache_version='invalid')
                self.assertEqual(cache.load_from_cache(path), None)
                self.write_cache_file(path, cache_format='invalid')
                self.assertEqual(cache.load_from_cache(path), None)
                self.write_file(path)
                self.assertEqual(cache.load_from_cache(path), None)
                self.assertEqual(cache.load_from_cache(None), None)

    def test_generate_and_cache(self):
        with self.tempdir() as path:
            subdir = os.path.join(path, 'subdirectory')
            path = os.path.join(subdir, 'db.bin')
            data = cache.generate_and_cache(path)
            self.assertEqual(cache.load_from_cache(path), data)

            with self.assertWarningText('unable'):
                self.assertEqual(cache.generate_and_cache(subdir), data)

            with self.assertNoWarning():
                self.assertEqual(cache.generate_and_cache(None), data)
