from unittest import TestCase
import futsu.io as io
import tempfile
import os

class TestIo(TestCase):

    def test_read_line_list(self):
        line_list = io.read_line_list(os.path.join('futsu','test','test_io_0.txt'))
        self.assertEqual(line_list,['qwer','asdf'])

        line_list = io.read_line_list(os.path.join('futsu','test','test_io_1.txt'))
        self.assertEqual(line_list,['qwer','asdf'])

        line_list = io.read_line_list(os.path.join('futsu','test','test_io_2.txt'))
        self.assertEqual(line_list,['qwer','asdf',''])

    def test_write_line_list(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'PRXNBTESJS')

            line_list = ['qwer','asdf']
            io.write_line_list(tmp_filename, line_list)
            self.assertEqual(line_list,['qwer','asdf'])

            line_list = ['qwer','asdf','']
            io.write_line_list(tmp_filename, line_list)
            self.assertEqual(line_list,['qwer','asdf',''])
