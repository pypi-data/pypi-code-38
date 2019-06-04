#!/usr/bin/python
# -*- coding: utf-8 -*-
"""File used to unit test the pacifica archive interface."""
import unittest
import os
from pacifica.archiveinterface.backends.posix.extendedfile import extended_file_factory
from pacifica.archiveinterface.backends.posix.status import PosixStatus
from .common_setup_test import SetupTearDown


class TestExtendedFile(unittest.TestCase, SetupTearDown):
    """Test the ExtendedFile Class."""

    def test_posix_file_status(self):
        """Test the correct values of a files status."""
        filepath = '{}{}'.format(os.path.sep, os.path.join('tmp', '1234'))
        my_file = extended_file_factory(filepath, 'w')
        status = my_file.status()
        self.assertTrue(isinstance(status, PosixStatus))
        self.assertEqual(status.filesize, 0)
        self.assertEqual(status.file_storage_media, 'disk')
        my_file.close()

    def test_posix_file_stage(self):
        """Test the correct staging of a posix file."""
        filepath = '{}{}'.format(os.path.sep, os.path.join('tmp', '1234'))
        mode = 'w'
        my_file = extended_file_factory(filepath, mode)
        my_file.stage()
        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        self.assertTrue(my_file._staged)
        # pylint: enable=protected-access
        my_file.close()


class TestPosixStatus(unittest.TestCase, SetupTearDown):
    """Test the POSIXStatus Class."""

    def test_posix_status_object(self):
        """Test the correct creation of posix status object."""
        status = PosixStatus(0o36, 0o35, 15, 15)
        self.assertEqual(status.mtime, 0o36)
        self.assertEqual(status.ctime, 0o35)
        self.assertEqual(status.bytes_per_level, 15)
        self.assertEqual(status.filesize, 15)
        self.assertEqual(status.defined_levels, ['disk'])
        self.assertEqual(status.file_storage_media, 'disk')

    def test_posix_status_storage_media(self):
        """Test the correct finding of posix storage media."""
        status = PosixStatus(0o36, 0o35, 15, 15)
        value = status.find_file_storage_media()
        self.assertEqual(value, 'disk')

    def test_posix_status_levels(self):
        """Test the correct setting of file storage levels."""
        status = PosixStatus(0o36, 0o35, 15, 15)
        value = status.define_levels()
        self.assertEqual(value, ['disk'])
