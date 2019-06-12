from __future__ import unicode_literals

import os
import shutil
import tempfile

import unix_ar

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class _BaseTestInTempDir(object):
    @classmethod
    def setUpClass(cls):
        cls._dir = tempfile.mkdtemp(prefix='unix_ar_test_')
        os.chdir(cls._dir)

    @classmethod
    def tearDownClass(cls):
        os.chdir('/')
        shutil.rmtree(cls._dir)


class TestWrite(unittest.TestCase, _BaseTestInTempDir):
    @classmethod
    def setUpClass(cls):
        _BaseTestInTempDir.setUpClass()
        with open('h.txt', 'wb') as fp:
            fp.write(b'hello,\n')
        with open('w.txt', 'wb') as fp:
            fp.write(b'world\n')

    def assertEqualExceptTwos(self, value, expected):
        if len(value) != len(expected):
            raise AssertionError("%r != %r (lengths don't match)" % (
                                 value, expected))
        two = b'2'[0]  # PY3 workaround
        for i, (v, e) in enumerate(zip(value, expected)):
            if e != two and v != e:
                raise AssertionError("%r != %r (first mismatch at %d)" % (
                                     value, expected, i))

    def test_empty(self):
        archive = unix_ar.open('empty.ar', 'w')
        with self.assertRaises(ValueError) as cm:
            archive.infolist()
        self.assertEqual(cm.exception.args[0],
                         "Can't read from a write-only archive")
        archive.close()

        with open('empty.ar', 'rb') as fp:
            self.assertEqual(fp.read(),
                             b'!<arch>\n')

    def test_add(self):
        archive = unix_ar.open('add.ar', 'w')
        archive.add('h.txt', arcname='he')
        archive.add('w.txt')
        archive.close()

        with open('add.ar', 'rb') as fp:
            self.assertEqualExceptTwos(
                fp.read(),
                b'!<arch>\n'
                b'he              2222222222  2222  '
                b'2222  100622  7         `\n'
                b'hello,\n'
                b'\n'
                b'w.txt           2222222222  2222  '
                b'2222  100622  6         `\n'
                b'world\n')

        with self.assertRaises(ValueError) as cm:
            archive.add('h.txt')
        self.assertEqual(cm.exception.args[0],
                         "Attempted to use a closed ArFile")

    def test_addfile(self):
        archive = unix_ar.open('addfile.ar', 'w')
        archive.addfile(unix_ar.ArInfo('w.txt', size=4))
        with open('h.txt', 'rb') as fp:
            archive.addfile('w.txt', fp)
        archive.close()

        with open('addfile.ar', 'rb') as fp:
            self.assertEqualExceptTwos(
                fp.read(),
                b'!<arch>\n'
                b'w.txt           2222222222  2222  '
                b'2222  100622  4         `\n'
                b'worl'
                b'w.txt           2222222222  2222  '
                b'2222  100622  6         `\n'
                b'hello,')


class TestRead(_BaseTestInTempDir, unittest.TestCase):
    def test_extract(self):
        with open('archive.ar', 'wb') as fp:
            fp.write(
                b'!<arch>\n'
                b'h.txt           1464380987  501   '
                b'20    100644  7         `\n'
                b'hello,\n'
                b'\n'
                b'w.txt           1464380990  501   '
                b'20    100644  6         `\n'
                b'world\n')

        archive = unix_ar.open('archive.ar', 'r')
        with self.assertRaises(ValueError) as cm:
            archive.add('/etc/passwd')
        self.assertEqual(cm.exception.args[0],
                         "Can't change a read-only archive")
        self.assertEqual(
            [(e.name, e.size, e.mtime, e.perms, e.uid, e.gid, e.offset)
             for e in archive.infolist()],
            [(b'h.txt', 7, 1464380987, 0o100644, 501, 20, 8),
             (b'w.txt', 6, 1464380990, 0o100644, 501, 20, 8 + 60 + 8)])

        info = archive.getinfo(b'w.txt')
        self.assertEqual(
            (info.name, info.size, info.mtime,
             info.perms, info.uid, info.gid, info.offset),
            (b'w.txt', 6, 1464380990, 0o100644, 501, 20, 8 + 60 + 8))

        archive.extract(info)
        with open('w.txt', 'rb') as fp:
            self.assertEqual(fp.read(), b'world\n')

        os.mkdir('sub')

        archive.extract('h.txt', b'sub')
        with open('sub/h.txt', 'rb') as fp:
            self.assertEqual(fp.read(), b'hello,\n')

        info.name = 'sub/other.txt'
        info.size = 3
        archive.extract(info)
        with open('sub/other.txt', 'rb') as fp:
            self.assertEqual(fp.read(), b'wor')

        os.mkdir('all')

        archive.extractall('all')
        with open('all/h.txt', 'rb') as fp:
            self.assertEqual(fp.read(), b'hello,\n')
        with open('all/w.txt', 'rb') as fp:
            self.assertEqual(fp.read(), b'world\n')

        archive.close()


if __name__ == '__main__':
    unittest.main()
