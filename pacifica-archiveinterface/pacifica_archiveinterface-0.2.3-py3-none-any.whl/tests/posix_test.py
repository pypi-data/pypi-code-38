#!/usr/bin/python
# -*- coding: utf-8 -*-
"""File used to unit test the pacifica archive interface."""
import unittest
import os
from stat import ST_MODE
from six import PY2
from pacifica.archiveinterface.archive_utils import bytes_type
from pacifica.archiveinterface.backends.posix.archive import PosixBackendArchive
import pacifica.archiveinterface.config as pa_config
from .common_setup_test import SetupTearDown


class TestPosixBackendArchive(unittest.TestCase, SetupTearDown):
    """Test the Posix backend archive."""

    def test_posix_backend_create(self):
        """Test creating a posix backend."""
        backend = PosixBackendArchive('/tmp')
        self.assertTrue(isinstance(backend, PosixBackendArchive))
        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        self.assertEqual(backend._prefix, '/tmp')
        # pylint: enable=protected-access

    def test_posix_backend_open(self):
        """Test opening a file from posix backend."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp')
        my_file = backend.open(filepath, mode)
        self.assertTrue(isinstance(my_file, PosixBackendArchive))
        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        self.assertEqual(backend._file.__class__.__name__, 'ExtendedFile')
        # pylint: enable=protected-access
        my_file.close()

    def test_posix_backend_stage(self):
        """Test staging a file from posix backend."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp')
        my_file = backend.open(filepath, mode)
        my_file.stage()
        # pylint: disable=protected-access
        self.assertTrue(my_file._file._staged)
        # pylint: enable=protected-access
        my_file.close()

    def test_posix_backend_open_twice(self):
        """Test opening a file from posix backend twice."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp')
        my_file = backend.open(filepath, mode)
        my_file = backend.open(filepath, mode)
        self.assertTrue(isinstance(my_file, PosixBackendArchive))
        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        self.assertEqual(backend._file.__class__.__name__, 'ExtendedFile')
        # pylint: enable=protected-access
        my_file.close()

    def test_posix_backend_open_id2f(self):
        """Test opening a file from posix backend twice."""
        backend = PosixBackendArchive('/tmp')
        mode = 'w'
        my_file = backend.open('/a/b/d', mode)
        temp_cfg_file = pa_config.CONFIG_FILE
        pa_config.CONFIG_FILE = 'test_configs/posix-id2filename.cfg'
        backend = PosixBackendArchive('/tmp')
        my_file = backend.open(12345, mode)
        my_file.write('this is file 12345')
        my_file.close()
        # pylint: disable=protected-access
        my_file.patch(123456789, '/tmp{}'.format(my_file._id2filename(12345)))
        # pylint: enable=protected-access
        my_file = backend.open(123456789, 'r')
        text = my_file.read(-1)
        pa_config.CONFIG_FILE = temp_cfg_file
        self.assertTrue(isinstance(my_file, PosixBackendArchive))
        self.assertEqual(bytes_type('this is file 12345'), text)
        my_file.close()

    def test_posix_backend_close(self):
        """Test closing a file from posix backend."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open(filepath, mode)
        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        self.assertEqual(backend._file.__class__.__name__, 'ExtendedFile')
        my_file.close()
        self.assertEqual(backend._file, None)
        # pylint: enable=protected-access

    def test_posix_backend_write(self):
        """Test writing a file from posix backend."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open(filepath, mode)
        error = my_file.write('i am a test string')
        if PY2:
            self.assertEqual(error, None)
        else:
            self.assertEqual(error, 18)
        my_file.close()

    def test_posix_file_mod_time(self):
        """Test the correct setting of a file mod time."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open(filepath, mode)
        my_file.close()
        my_file.set_mod_time(1000000)
        my_file = backend.open(filepath, 'r')
        status = my_file.status()
        my_file.close()
        self.assertEqual(status.mtime, 1000000)

    def test_posix_file_permissions(self):
        """Test the correct setting of a file mod time."""
        filepath = '12345'
        mode = 'w'
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open(filepath, mode)
        my_file.close()
        my_file.set_file_permissions()
        statinfo = oct(os.stat('/tmp/12345')[ST_MODE])[-3:]
        self.assertEqual(statinfo, '444')

    def test_posix_backend_read(self):
        """Test reading a file from posix backend."""
        self.test_posix_backend_write()
        filepath = '1234'
        mode = 'r'
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open(filepath, mode)
        buf = my_file.read(-1)
        self.assertEqual(buf, bytes_type('i am a test string'))
        my_file.close()

    def test_patch(self):
        """Test patching file."""
        old_path = '/tmp/1234'
        backend = PosixBackendArchive('/tmp')
        my_file = backend.open('1234', 'w')
        my_file.close()
        backend.patch('5678', '/tmp/1234')
        # Error would be thrown on patch so nothing to assert
        self.assertEqual(old_path, '/tmp/1234')
