import os
import tempfile
import shutil

from django.core import management
from django.test import TestCase


class TestDumpDbAsJson(TestCase):
    def __remove_dumpdata_directory(self):
        if os.path.exists(self.dumpdata_directory):
            shutil.rmtree(self.dumpdata_directory)

    def setUp(self):
        self.dumpdata_directory = tempfile.mkdtemp()
        self.dumpdata_file = os.path.join(self.dumpdata_directory, 'default.sql')
        self.__remove_dumpdata_directory()

    def tearDown(self):
        self.__remove_dumpdata_directory()

    def test_dumpfile_created(self):
        self.assertFalse(os.path.exists(self.dumpdata_file))
        with self.settings(IEVVTASKS_DUMPDATA_DIRECTORY=self.dumpdata_directory):
            management.call_command('ievvtasks_dump_db_as_sql')
        self.assertTrue(os.path.exists(self.dumpdata_file))
