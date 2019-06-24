import os
from django.test import TestCase
from ievv_opensource.utils import virtualenvutils
from ievv_opensource.python2_compatibility import mock


class TestVirtualenvUtils(TestCase):
    def test_is_in_virtualenv_true(self):
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys.real_prefix',
                        '/something'):
            self.assertTrue(virtualenvutils.is_in_virtualenv())

    def test_is_in_virtualenv_false(self):
        class NoAttributes:
            pass
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys', NoAttributes):
            self.assertFalse(virtualenvutils.is_in_virtualenv())

    def test_get_virtualenv_directory_not_in_virtualenv(self):
        class NoAttributes:
            pass
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys', NoAttributes):
            with self.assertRaises(OSError):
                virtualenvutils.get_virtualenv_directory()

    def test_get_virtualenv_directory_is_in_virtualenv(self):
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys.real_prefix',
                        '/real'):
            with mock.patch('ievv_opensource.utils.virtualenvutils.sys.prefix',
                            '/virtual'):
                self.assertEqual('/virtual',
                                 virtualenvutils.get_virtualenv_directory())

    def test_add_virtualenv_bin_directory_to_path(self):
        mockenviron = {'PATH': ''}
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys.real_prefix',
                        '/real'):
            with mock.patch('ievv_opensource.utils.virtualenvutils.sys.prefix',
                            '/virtual'):
                with mock.patch('ievv_opensource.utils.virtualenvutils.os.environ',
                                mockenviron):
                    virtualenvutils.add_virtualenv_bin_directory_to_path()
        self.assertEqual('{}/virtual/bin'.format(os.pathsep),
                         mockenviron['PATH'])
