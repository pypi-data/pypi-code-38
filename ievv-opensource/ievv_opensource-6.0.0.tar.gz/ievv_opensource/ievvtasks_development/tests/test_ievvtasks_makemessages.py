import os
import shutil
import unittest

from django.conf import settings

from django.core import management
from django.test import TestCase


@unittest.skip('This does not work as intended')
class TestMakemessages(TestCase):
    def __remove_locale_directory(self):
        if os.path.exists(self.locale_directory):
            shutil.rmtree(self.locale_directory)

    def setUp(self):
        self.locale_directory = settings.LOCALE_PATHS[0]
        self.locale_paths = [self.locale_directory]
        self.__remove_locale_directory()

    def tearDown(self):
        self.__remove_locale_directory()

    def test_locale_directory_created(self):
        self.assertFalse(os.path.exists(self.locale_directory))
        with self.settings(LOCALE_PATHS=self.locale_paths):
            management.call_command('ievvtasks_makemessages')
        self.assertTrue(os.path.exists(self.locale_directory))

    def test_po_file_created(self):
        po_file_path = os.path.join(self.locale_directory,
                                    'en', 'LC_MESSAGES', 'django.po')
        self.assertFalse(os.path.exists(po_file_path))
        with self.settings(IEVVTASKS_MAKEMESSAGES_LANGUAGE_CODES=['en']):
            management.call_command('ievvtasks_makemessages')
        self.assertTrue(os.path.exists(self.locale_directory))
        self.assertTrue(os.path.exists(po_file_path))
