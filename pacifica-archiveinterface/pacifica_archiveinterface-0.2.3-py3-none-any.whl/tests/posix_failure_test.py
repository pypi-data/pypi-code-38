#!/usr/bin/python
# -*- coding: utf-8 -*-
"""File used to unit test the pacifica archive interface."""
import unittest
import mock
from pacifica.archiveinterface.backends.posix.archive import PosixBackendArchive
from pacifica.archiveinterface.exception import ArchiveInterfaceError
from .common_setup_test import SetupTearDown


class TestPosixBackendArchive(unittest.TestCase, SetupTearDown):
    """Test the Posix backend archive."""

    def test_posix_backend_error(self):
        """Test opening a file from posix backend."""
        with self.assertRaises(ArchiveInterfaceError):
            backend = PosixBackendArchive('/tmp')
            # easiest way to unit test is look at class variable
            # pylint: disable=protected-access
            backend._file = 'none file object'
            backend.open('1234', 'w')
            # pylint: enable=protected-access

    @mock.patch('os.utime')
    def test_posix_file_mod_time_failed(self, mock_utime):
        """Test the correct setting of a file mod time."""
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open('1234', 'w')
        my_file.close()
        mock_utime.side_effect = OSError('Unable to set utime.')
        with self.assertRaises(ArchiveInterfaceError) as exc:
            my_file.set_mod_time(1000000)
        self.assertTrue("Can't set posix file mod time with error" in str(exc.exception))

    @mock.patch('os.chmod')
    def test_posix_file_perms_failed(self, mock_chmod):
        """Test the correct setting of a file mod time."""
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open('1235', 'w')
        my_file.close()
        mock_chmod.side_effect = OSError('Unable to chmod.')
        with self.assertRaises(ArchiveInterfaceError) as exc:
            my_file.set_file_permissions()
        self.assertTrue("Can't set posix file permissions with error" in str(exc.exception))

    def test_posix_backend_failed_write(self):
        """Test writing to a failed file."""
        backend = PosixBackendArchive('/tmp/')
        # test failed write
        backend.open('1234', 'w')

        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file.write = mock.MagicMock(side_effect=IOError('Unable to Write!'))
        # pylint: enable=protected-access
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.write('write stuff')
        self.assertTrue("Can't write posix file with error" in str(exc.exception))
        backend.close()

    def test_posix_backend_failed_stat(self):
        """Test status to a failed file."""
        backend = PosixBackendArchive('/tmp/')
        backend.open('1234', 'w')
        backend.close()
        # test failed write
        backend.open('1234', 'r')

        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file.status = mock.MagicMock(side_effect=IOError('Unable to Read!'))
        # pylint: enable=protected-access
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.status()
        self.assertTrue("Can't get posix file status with error" in str(exc.exception))
        backend.close()

    def test_posix_backend_failed_read(self):
        """Test reading to a failed file."""
        backend = PosixBackendArchive('/tmp/')
        backend.open('1234', 'w')
        backend.close()
        # test failed write
        backend.open('1234', 'r')

        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file.read = mock.MagicMock(side_effect=IOError('Unable to Read!'))
        # pylint: enable=protected-access
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.read(1024)
        self.assertTrue("Can't read posix file with error" in str(exc.exception))
        backend.close()

    def test_posix_backend_failed_fd(self):
        """Test reading to a failed file fd."""
        backend = PosixBackendArchive('/tmp/')
        # test failed write
        backend.open('1234', 'w')

        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file = None
        # pylint: enable=protected-access
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.write('Something to write')
        self.assertTrue('Internal file handle invalid' in str(exc.exception))
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.read(1024)
        self.assertTrue('Internal file handle invalid' in str(exc.exception))
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.stage()
        self.assertTrue('Internal file handle invalid' in str(exc.exception))
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.status()
        self.assertTrue('Internal file handle invalid' in str(exc.exception))

    def test_posix_backend_failed_stage(self):
        """Test reading a file from posix backend."""
        backend = PosixBackendArchive('/tmp/')
        backend.open('1234', 'w')
        backend.close()
        backend.open('1234', 'r')
        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file.stage = mock.MagicMock(side_effect=IOError('Unable to Stage!'))
        # pylint: enable=protected-access
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.stage()
        self.assertTrue('Can\'t stage posix file with error' in str(exc.exception))
        backend.close()

    @mock.patch('shutil.move')
    def test_patch_failed(self, mock_move):
        """Test patching file."""
        mock_move.side_effect = OSError('Unable to move')
        backend = PosixBackendArchive('/tmp')
        my_file = backend.open('1234', 'w')
        my_file.close()
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.patch('5678', '/tmp/1234')
        self.assertTrue('Can\'t move posix file with error' in str(exc.exception))

    @mock.patch('os.unlink')
    def test_delete_failed(self, mock_unlink):
        """Test patching file."""
        mock_unlink.side_effect = OSError('Unable to delete')
        backend = PosixBackendArchive('/tmp')
        my_file = backend.open('1234', 'w')
        my_file.close()
        with self.assertRaises(ArchiveInterfaceError) as exc:
            backend.remove()
        self.assertTrue('Can\'t remove posix file with error' in str(exc.exception))
