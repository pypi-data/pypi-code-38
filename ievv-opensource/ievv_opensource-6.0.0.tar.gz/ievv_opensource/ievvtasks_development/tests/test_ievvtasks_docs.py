import os
import shutil
import unittest

from django.core import management
from django.core.management import CommandError
from django.test import TestCase

from ievv_opensource.utils import virtualenvutils
from ievv_opensource.python2_compatibility import mock


@unittest.skip('This is both slow and hard to ensure works in different environments')
class TestDocs(TestCase):
    def __remove_documentation_build_directory(self):
        if os.path.exists(self.documentation_build_directory):
            shutil.rmtree(self.documentation_build_directory)

    def setUp(self):
        self.documentation_build_directory = 'test_documentation_build_directory'
        self.__remove_documentation_build_directory()
        virtualenvutils.add_virtualenv_bin_directory_to_path()

    def tearDown(self):
        self.__remove_documentation_build_directory()

    def test_fail_if_build_clean_or_open_is_not_specified(self):
        with self.settings(IEVVTASKS_DOCS_BUILD_DIRECTORY=self.documentation_build_directory):
            with self.assertRaises(CommandError):
                management.call_command('ievvtasks_docs')

    def test_build(self):
        indexhtml_path = os.path.join(self.documentation_build_directory,
                                      'index.html')
        self.assertFalse(os.path.exists(indexhtml_path))
        with self.settings(IEVVTASKS_DOCS_BUILD_DIRECTORY=self.documentation_build_directory):
            management.call_command('ievvtasks_docs', build=True)
        self.assertTrue(os.path.exists(self.documentation_build_directory))
        self.assertTrue(os.path.exists(indexhtml_path))

    def test_clean(self):
        os.makedirs(self.documentation_build_directory)
        self.assertTrue(os.path.exists(self.documentation_build_directory))
        with self.settings(IEVVTASKS_DOCS_BUILD_DIRECTORY=self.documentation_build_directory):
            management.call_command('ievvtasks_docs', clean=True)
        self.assertFalse(os.path.exists(self.documentation_build_directory))

    def test_opendocs(self):
        openfile_mock = mock.MagicMock()
        with self.settings(IEVVTASKS_DOCS_BUILD_DIRECTORY=self.documentation_build_directory):
            with mock.patch('ievv_opensource.ievvtasks_development.management.commands.'
                            'ievvtasks_docs.open_file_with_default_os_opener',
                            openfile_mock):
                management.call_command('ievvtasks_docs', open=True)
        openfile_mock.assert_called_once_with(os.path.join(
            self.documentation_build_directory, 'index.html'))

    def test_clean_and_open_not_build_fails(self):
        with self.settings(IEVVTASKS_DOCS_BUILD_DIRECTORY=self.documentation_build_directory):
            with self.assertRaises(CommandError):
                management.call_command('ievvtasks_docs', open=True, clean=True, build=False)
