#!/usr/bin/python
# -*- coding: utf-8 -*-
"""File used to unit test the pacifica archive interface."""
from json import loads
import unittest
import time
from pacifica.archiveinterface.archive_utils import un_abs_path, get_http_modified_time
from pacifica.archiveinterface.id2filename import id2filename
from pacifica.archiveinterface.exception import ArchiveInterfaceError
from pacifica.archiveinterface.rest_generator import ArchiveInterfaceGenerator
from pacifica.archiveinterface.backends.factory import ArchiveBackendFactory
from .common_setup_test import SetupTearDown


class TestArchiveUtils(unittest.TestCase, SetupTearDown):
    """Test the Archive utils class."""

    def test_utils_absolute_path(self):
        """Test the return of un_abs_path."""
        return_one = un_abs_path('tmp/foo.text')
        return_two = un_abs_path('/tmp/foo.text')
        return_three = un_abs_path('/tmp/foo.text')
        return_four = un_abs_path('foo.text')
        self.assertEqual(return_one, 'tmp/foo.text')
        self.assertEqual(return_two, 'tmp/foo.text')
        self.assertNotEqual(return_three, '/tmp/foo.text')
        self.assertEqual(return_four, 'foo.text')
        hit_exception = False
        try:
            un_abs_path(47)
        except ArchiveInterfaceError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_get_http_modified_time(self):
        """Test to see if the path size of a directory is returned."""
        env = dict()
        env['HTTP_LAST_MODIFIED'] = 'SUN, 06 NOV 1994 08:49:37 GMT'
        mod_time = get_http_modified_time(env)
        self.assertEqual(mod_time, 784111777)
        env = dict()
        mod_time = get_http_modified_time(env)
        self.assertEqual(int(mod_time), int(time.time()))
        for thing in (None, [], 46):
            hit_exception = False
            try:
                env['HTTP_LAST_MODIFIED'] = thing
                get_http_modified_time(env)
            except ArchiveInterfaceError:
                hit_exception = True
            self.assertTrue(hit_exception)


class TestId2Filename(unittest.TestCase, SetupTearDown):
    """Test the id2filename method."""

    def test_id2filename_basic(self):
        """Test the correct creation of a basicfilename."""
        filename = id2filename(1234)
        self.assertEqual(filename, '/d2/4d2')

    def test_id2filename_negative(self):
        """Test the correct creation of a negative filename."""
        filename = id2filename(-1)
        self.assertEqual(filename, '/file.-1')

    def test_id2filename_zero(self):
        """Test the correct creation of a zero filename."""
        filename = id2filename(0)
        self.assertEqual(filename, '/file.0')

    def test_id2filename_simple(self):
        """Test the correct creation of a simple filename."""
        filename = id2filename(1)
        self.assertEqual(filename, '/file.1')

    def test_id2filename_u_shift_point(self):
        """Test the correct creation of an under shift point filename."""
        filename = id2filename((32 * 1024) - 1)
        self.assertEqual(filename, '/ff/7fff')

    def test_id2filename_shift_point(self):
        """Test the correct creation of the shift point filename."""
        filename = id2filename((32 * 1024))
        self.assertEqual(filename, '/00/8000')

    def test_id2filename_o_shift_point(self):
        """Test the correct creation of an over shift point filename."""
        filename = id2filename((32 * 1024) + 1)
        self.assertEqual(filename, '/01/8001')


class TestBackendArchive(unittest.TestCase, SetupTearDown):
    """Test the backend archive."""

    def test_posix_backend(self):
        """Test the creation of a posix backend."""
        factory = ArchiveBackendFactory()
        backend = factory.get_backend_archive('posix', '/tmp')
        # pylint: disable=protected-access
        prefix = backend._prefix
        # pylint: enable=protected-access
        self.assertEqual('/tmp', prefix)

    def test_invalid_backend(self):
        """Test the creation of an invalid backend."""
        with self.assertRaises(NotImplementedError):
            factory = ArchiveBackendFactory()
            factory.get_backend_archive('badbackend', '/tmp')


class TestArchiveGenerator(unittest.TestCase, SetupTearDown):
    """Test the archive generator."""

    @staticmethod
    def start_response(code, headers):
        """Method to mock start_response."""
        return [code, headers]

    def test_generator_creation(self):
        """Test the creation of a archive generator."""
        factory = ArchiveBackendFactory()
        backend = factory.get_backend_archive('posix', '/tmp')
        generator = ArchiveInterfaceGenerator(backend)
        # pylint: disable=protected-access
        archive = generator._archive
        # pylint: enable=protected-access
        self.assertEqual(backend, archive)

    def test_generator_get(self):
        """Test the creation of a archive generator."""
        factory = ArchiveBackendFactory()
        backend = factory.get_backend_archive('posix', '/tmp')
        generator = ArchiveInterfaceGenerator(backend)
        jsn = loads(generator.GET())
        self.assertEqual(
            jsn['message'], 'Pacifica Archive Interface Up and Running')
